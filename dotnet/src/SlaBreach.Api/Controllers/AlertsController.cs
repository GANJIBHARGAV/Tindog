using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using SlaBreach.Domain.Entities;
using SlaBreach.Infrastructure.Notifications;
using SlaBreach.Infrastructure.Persistence;

namespace SlaBreach.Api.Controllers;

[ApiController]
[Route("api/alerts")]
public class AlertsController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly NotificationService _notify;
    public AlertsController(AppDbContext db, NotificationService notify) { _db = db; _notify = notify; }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<Alert>>> List()
    {
        var items = await _db.Alerts.OrderByDescending(a => a.CreatedAt).ToListAsync();
        return Ok(items);
    }

    [HttpPost("{id:int}/resend")]
    public async Task<IActionResult> Resend(int id)
    {
        var alert = await _db.Alerts.FindAsync(id);
        if (alert is null) return NotFound();
        // For simplicity, assume routing contains emails
        var route = alert.RoutingJson;
        var emails = new List<string>();
        try
        {
            if (!string.IsNullOrWhiteSpace(route))
            {
                var doc = System.Text.Json.JsonDocument.Parse(route);
                if (doc.RootElement.TryGetProperty("email", out var arr) && arr.ValueKind == System.Text.Json.JsonValueKind.Array)
                {
                    foreach (var e in arr.EnumerateArray()) emails.Add(e.GetString() ?? "");
                }
            }
        }
        catch { }
        if (emails.Count > 0) _notify.SendEmail(emails, $"RESEND: SLA {alert.State}", alert.Message);
        return Ok(new { ok = true });
    }
}
