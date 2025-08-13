using System;
using System.Linq;
using Microsoft.EntityFrameworkCore;
using SlaBreach.Domain;
using SlaBreach.Domain.Entities;
using SlaBreach.Infrastructure.Persistence;

namespace SlaBreach.Infrastructure.Services;

public class SlaEvaluator
{
    private const double AtRiskMargin = 0.9;
    private readonly AppDbContext _db;

    public SlaEvaluator(AppDbContext db)
    {
        _db = db;
    }

    private static bool Compare(Comparator comparator, double value, double threshold)
    {
        return comparator switch
        {
            Comparator.Gt => value > threshold,
            Comparator.Gte => value >= threshold,
            Comparator.Lt => value < threshold,
            Comparator.Lte => value <= threshold,
            _ => throw new ArgumentOutOfRangeException(nameof(comparator))
        };
    }

    private static bool AtRisk(Comparator comparator, double value, double threshold)
    {
        return comparator is Comparator.Gt or Comparator.Gte
            ? value > threshold * AtRiskMargin
            : value < threshold / AtRiskMargin;
    }

    public (SlaStatus status, Alert? alert) Evaluate(Sla sla)
    {
        var now = DateTimeOffset.UtcNow;
        var windowStart = now.AddMinutes(-sla.WindowMinutes);

        var agg = _db.Events
            .Where(e => e.Service == sla.Service && e.MetricType == sla.MetricType && e.EventTs >= windowStart)
            .Select(e => (double?)e.Value)
            .Average();

        var status = _db.SlaStatuses.FirstOrDefault(s => s.SlaId == sla.Id);
        if (status == null)
        {
            status = new SlaStatus { SlaId = sla.Id };
            _db.SlaStatuses.Add(status);
            _db.SaveChanges();
        }

        var previous = status.State;
        var newState = SlaStatusState.Normal;
        Alert? alert = null;

        var value = agg ?? status.LastValue ?? 0.0;
        if (agg is not null)
        {
            if (Compare(sla.Comparator, value, sla.Threshold))
            {
                newState = SlaStatusState.Breached;
                if (previous != SlaStatusState.Breached)
                {
                    alert = new Alert
                    {
                        SlaId = sla.Id,
                        State = AlertState.Breached,
                        Message = $"SLA '{sla.Name}' is breached (avg={value:F2}, threshold={sla.Threshold})",
                        Severity = sla.Severity.ToString(),
                        RoutingJson = System.Text.Json.JsonSerializer.Serialize(sla.NotificationRules)
                    };
                    _db.Alerts.Add(alert);
                }
            }
            else if (AtRisk(sla.Comparator, value, sla.Threshold))
            {
                newState = SlaStatusState.AtRisk;
                if (previous == SlaStatusState.Normal)
                {
                    alert = new Alert
                    {
                        SlaId = sla.Id,
                        State = AlertState.AtRisk,
                        Message = $"SLA '{sla.Name}' is at risk (avg={value:F2}, threshold={sla.Threshold})",
                        Severity = sla.Severity.ToString(),
                        RoutingJson = System.Text.Json.JsonSerializer.Serialize(sla.NotificationRules)
                    };
                    _db.Alerts.Add(alert);
                }
            }
            else
            {
                if (previous is SlaStatusState.AtRisk or SlaStatusState.Breached)
                {
                    newState = SlaStatusState.Recovered;
                    alert = new Alert
                    {
                        SlaId = sla.Id,
                        State = AlertState.Recovered,
                        Message = $"SLA '{sla.Name}' recovered (avg={value:F2}, threshold={sla.Threshold})",
                        Severity = sla.Severity.ToString(),
                        RoutingJson = System.Text.Json.JsonSerializer.Serialize(sla.NotificationRules)
                    };
                    _db.Alerts.Add(alert);
                }
                else
                {
                    newState = SlaStatusState.Normal;
                }
            }
        }

        status.State = newState;
        status.LastValue = value;
        status.UpdatedAt = DateTimeOffset.UtcNow;
        _db.SaveChanges();

        return (status, alert);
    }
}
