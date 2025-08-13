using Hangfire;
using Hangfire.PostgreSql;
using Microsoft.EntityFrameworkCore;
using SlaBreach.Infrastructure.Jobs;
using SlaBreach.Infrastructure.Persistence;

namespace SlaBreach.Api.Configuration;

public static class ServiceExtensions
{
    public static IServiceCollection AddHangfireScheduler(this IServiceCollection services, IConfiguration cfg)
    {
        var conn = cfg.GetConnectionString("Default")!;
        services.AddHangfire(c => c.UseSimpleAssemblyNameTypeSerializer().UseRecommendedSerializerSettings().UsePostgreSqlStorage(conn));
        services.AddHangfireServer();
        services.AddScoped<Scheduler>();
        return services;
    }

    public static IApplicationBuilder UseRecurringSlaEvaluation(this IApplicationBuilder app)
    {
        using var scope = app.ApplicationServices.CreateScope();
        var scheduler = scope.ServiceProvider.GetRequiredService<Scheduler>();
        RecurringJob.AddOrUpdate("evaluate-slas", () => scheduler.EvaluateAllSlas(), Cron.Minutely);
        return app;
    }
}
