using System;

namespace SlaBreach.Domain.Entities;

public class Event
{
    public int Id { get; set; }
    public string Service { get; set; } = string.Empty;
    public string MetricType { get; set; } = string.Empty;
    public double Value { get; set; }
    public DateTimeOffset EventTs { get; set; } = DateTimeOffset.UtcNow;
    public string? IdempotencyKey { get; set; }
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
}