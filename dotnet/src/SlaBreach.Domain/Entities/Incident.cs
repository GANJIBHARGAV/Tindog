using System;
using SlaBreach.Domain;

namespace SlaBreach.Domain.Entities;

public class Incident
{
    public int Id { get; set; }
    public int SlaId { get; set; }
    public Sla? Sla { get; set; }
    public IncidentStatus Status { get; set; } = IncidentStatus.Open;
    public string Severity { get; set; } = "Medium";
    public DateTimeOffset StartedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset? AcknowledgedAt { get; set; }
    public int? AcknowledgedBy { get; set; }
    public DateTimeOffset? ResolvedAt { get; set; }
    public string? Owner { get; set; }
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
}

public enum AlertState { AtRisk, Breached, Recovered }

public class Alert
{
    public int Id { get; set; }
    public int? IncidentId { get; set; }
    public Incident? Incident { get; set; }
    public int SlaId { get; set; }
    public Sla? Sla { get; set; }
    public AlertState State { get; set; }
    public string Message { get; set; } = string.Empty;
    public string Severity { get; set; } = "Medium";
    public string? RoutingJson { get; set; }
    public DateTimeOffset SentAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
}

public class DeliveryLog
{
    public int Id { get; set; }
    public int AlertId { get; set; }
    public Alert? Alert { get; set; }
    public string Provider { get; set; } = string.Empty; // email, slack, sms
    public string Status { get; set; } = string.Empty;   // success, failed
    public string? ErrorMessage { get; set; }
    public int Attempts { get; set; } = 0;
    public DateTimeOffset? NextRetryAt { get; set; }
    public string? MetaJson { get; set; }
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
}

public class AuditLog
{
    public int Id { get; set; }
    public string TableName { get; set; } = string.Empty;
    public int RowId { get; set; }
    public string Action { get; set; } = string.Empty; // create, update, delete
    public string? ActorEmail { get; set; }
    public string? ChangesJson { get; set; }
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
}