using Hangfire;
using Microsoft.EntityFrameworkCore;
using SlaBreach.Infrastructure.Persistence;
using SlaBreach.Infrastructure.Services;

namespace SlaBreach.Infrastructure.Jobs;

public class Scheduler
{
    private readonly AppDbContext _db;
    private readonly SlaEvaluator _evaluator;

    public Scheduler(AppDbContext db, SlaEvaluator evaluator)
    {
        _db = db;
        _evaluator = evaluator;
    }

    [AutomaticRetry(Attempts = 0)]
    public async Task EvaluateAllSlas()
    {
        var slas = await _db.Slas.Where(s => !s.IsDeleted).ToListAsync();
        foreach (var sla in slas)
        {
            _evaluator.Evaluate(sla);
        }
    }
}
