using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using SlaBreach.Domain.Entities;
using SlaBreach.Infrastructure.Persistence;

namespace SlaBreach.Api.Controllers;

[ApiController]
[Route("api/incidents")]
public class IncidentsController : ControllerBase
{
    private readonly AppDbContext _db;
    public IncidentsController(AppDbContext db) { _db = db; }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<Incident>>> List()
    {
        var items = await _db.Incidents.OrderByDescending(i => i.CreatedAt).ToListAsync();
        return Ok(items);
    }

    [Authorize]
    [HttpPost("{id:int}/ack")]
    public async Task<IActionResult> Ack(int id)
    {
        var inc = await _db.Incidents.FindAsync(id);
        if (inc is null) return NotFound();
        inc.Status = SlaBreach.Domain.IncidentStatus.Acknowledged;
        await _db.SaveChangesAsync();
        return Ok(new { ok = true });
    }

    [Authorize]
    [HttpPost("{id:int}/resolve")]
    public async Task<IActionResult> Resolve(int id)
    {
        var inc = await _db.Incidents.FindAsync(id);
        if (inc is null) return NotFound();
        inc.Status = SlaBreach.Domain.IncidentStatus.Resolved;
        await _db.SaveChangesAsync();
        return Ok(new { ok = true });
    }
}
