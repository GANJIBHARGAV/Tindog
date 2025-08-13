using System;
using System.Collections.Generic;

namespace SlaBreach.Domain.Entities;

public class Calendar
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Timezone { get; set; } = "UTC";
    public List<BusinessHour> BusinessHours { get; set; } = new();
    public List<string> Holidays { get; set; } = new();
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
}

public class BusinessHour
{
    public string Day { get; set; } = "mon";
    public string Start { get; set; } = "09:00";
    public string End { get; set; } = "17:00";
}