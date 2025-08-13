using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Storage.ValueConversion;
using SlaBreach.Domain;
using SlaBreach.Domain.Entities;
using System.Text.Json;

namespace SlaBreach.Infrastructure.Persistence;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<User> Users => Set<User>();
    public DbSet<Calendar> Calendars => Set<Calendar>();
    public DbSet<Sla> Slas => Set<Sla>();
    public DbSet<SlaStatus> SlaStatuses => Set<SlaStatus>();
    public DbSet<Event> Events => Set<Event>();
    public DbSet<Incident> Incidents => Set<Incident>();
    public DbSet<Alert> Alerts => Set<Alert>();
    public DbSet<DeliveryLog> DeliveryLogs => Set<DeliveryLog>();
    public DbSet<AuditLog> AuditLogs => Set<AuditLog>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.HasPostgresExtension("uuid-ossp");

        modelBuilder.Entity<User>(e =>
        {
            e.HasIndex(x => x.Email).IsUnique();
        });

        modelBuilder.Entity<Event>(e =>
        {
            e.HasIndex(x => new { x.Service, x.MetricType, x.EventTs });
            e.HasIndex(x => x.IdempotencyKey).IsUnique();
        });

        modelBuilder.Entity<Sla>(e =>
        {
            e.Property(x => x.NotificationRules)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions?)null),
                    v => string.IsNullOrWhiteSpace(v) ? new() : JsonSerializer.Deserialize<Dictionary<string, object>>(v)!
                );
        });

        modelBuilder.Entity<Alert>(e =>
        {
            e.Property(x => x.RoutingJson);
        });

        modelBuilder.Entity<DeliveryLog>(e =>
        {
            e.Property(x => x.MetaJson);
        });
    }
}
