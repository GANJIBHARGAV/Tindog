using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using SlaBreach.Domain.Entities;
using SlaBreach.Infrastructure.Persistence;

namespace SlaBreach.Api.Controllers;

[ApiController]
[Route("api/slas")]
public class SlasController : ControllerBase
{
    private readonly AppDbContext _db;
    public SlasController(AppDbContext db) { _db = db; }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<Sla>>> List([FromQuery] string? service)
    {
        var q = _db.Slas.Where(s => !s.IsDeleted);
        if (!string.IsNullOrWhiteSpace(service)) q = q.Where(s => s.Service == service);
        var list = await q.OrderByDescending(s => s.CreatedAt).ToListAsync();
        return Ok(list);
    }

    [Authorize]
    [HttpPost]
    public async Task<ActionResult<Sla>> Create([FromBody] Sla payload)
    {
        _db.Slas.Add(payload);
        await _db.SaveChangesAsync();
        _db.SlaStatuses.Add(new SlaStatus { SlaId = payload.Id });
        await _db.SaveChangesAsync();
        return Ok(payload);
    }

    [HttpGet("{id:int}")]
    public async Task<ActionResult<Sla>> Get(int id)
    {
        var sla = await _db.Slas.FindAsync(id);
        if (sla is null || sla.IsDeleted) return NotFound();
        return Ok(sla);
    }

    [Authorize]
    [HttpPut("{id:int}")]
    public async Task<ActionResult<Sla>> Update(int id, [FromBody] Sla payload)
    {
        var sla = await _db.Slas.FindAsync(id);
        if (sla is null || sla.IsDeleted) return NotFound();
        _db.Entry(sla).CurrentValues.SetValues(payload);
        await _db.SaveChangesAsync();
        return Ok(sla);
    }

    [Authorize]
    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id)
    {
        var sla = await _db.Slas.FindAsync(id);
        if (sla is null || sla.IsDeleted) return NotFound();
        sla.IsDeleted = true;
        await _db.SaveChangesAsync();
        return Ok(new { ok = true });
    }

    [HttpGet("{id:int}/status")]
    public async Task<ActionResult<SlaStatus>> Status(int id)
    {
        var st = await _db.SlaStatuses.FirstOrDefaultAsync(s => s.SlaId == id);
        if (st is null) return NotFound();
        return Ok(st);
    }
}
