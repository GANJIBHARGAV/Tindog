using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using SlaBreach.Domain.Entities;
using SlaBreach.Infrastructure.Persistence;
using SlaBreach.Infrastructure.Services;

namespace SlaBreach.Api.Controllers;

[ApiController]
[Route("api/events")]
public class EventsController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly SlaEvaluator _evaluator;
    public EventsController(AppDbContext db, SlaEvaluator evaluator) { _db = db; _evaluator = evaluator; }

    public record EventIngest(string Service, string MetricType, double Value, DateTimeOffset? EventTs, string? IdempotencyKey);
    public record EventIngestBulk(IEnumerable<EventIngest> Events);

    [HttpPost("ingest")]
    public async Task<IActionResult> Ingest([FromBody] EventIngest evt, [FromHeader(Name = "x-idempotency-key")] string? key)
    {
        key ??= evt.IdempotencyKey;
        if (!string.IsNullOrEmpty(key))
        {
            if (await _db.Events.AnyAsync(e => e.IdempotencyKey == key))
                return Ok(new { ok = true, duplicate = true });
        }
        _db.Events.Add(new Event { Service = evt.Service, MetricType = evt.MetricType, Value = evt.Value, EventTs = evt.EventTs ?? DateTimeOffset.UtcNow, IdempotencyKey = key });
        await _db.SaveChangesAsync();
        // Evaluate all SLAs for simplicity
        foreach (var sla in _db.Slas.Where(s => !s.IsDeleted))
            _evaluator.Evaluate(sla);
        return Ok(new { ok = true });
    }

    [HttpPost("bulk")]
    public async Task<IActionResult> Bulk([FromBody] EventIngestBulk payload)
    {
        foreach (var ev in payload.Events)
        {
            if (!string.IsNullOrEmpty(ev.IdempotencyKey) && await _db.Events.AnyAsync(e => e.IdempotencyKey == ev.IdempotencyKey))
                continue;
            _db.Events.Add(new Event { Service = ev.Service, MetricType = ev.MetricType, Value = ev.Value, EventTs = ev.EventTs ?? DateTimeOffset.UtcNow, IdempotencyKey = ev.IdempotencyKey });
        }
        await _db.SaveChangesAsync();
        foreach (var sla in _db.Slas.Where(s => !s.IsDeleted))
            _evaluator.Evaluate(sla);
        return Ok(new { ok = true });
    }
}
