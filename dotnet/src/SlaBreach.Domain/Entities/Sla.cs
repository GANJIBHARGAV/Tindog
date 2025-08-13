using System;
using System.Collections.Generic;
using SlaBreach.Domain;

namespace SlaBreach.Domain.Entities;

public class Sla
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string Service { get; set; } = string.Empty;
    public string MetricType { get; set; } = string.Empty;
    public Comparator Comparator { get; set; } = Comparator.Lte;
    public double Threshold { get; set; }
    public int WindowMinutes { get; set; } = 5;
    public int GracePeriodSeconds { get; set; } = 0;
    public Severity Severity { get; set; } = Severity.Medium;
    public string? OwnerTeam { get; set; }
    public Dictionary<string, object> NotificationRules { get; set; } = new();
    public int? CalendarId { get; set; }
    public Calendar? Calendar { get; set; }
    public int SuppressionSeconds { get; set; } = 300;
    public bool IsDeleted { get; set; } = false;
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
}

public class SlaStatus
{
    public int Id { get; set; }
    public int SlaId { get; set; }
    public Sla? Sla { get; set; }
    public SlaStatusState State { get; set; } = SlaStatusState.Normal;
    public double? LastValue { get; set; }
    public long? SuppressionUntilTs { get; set; }
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
}