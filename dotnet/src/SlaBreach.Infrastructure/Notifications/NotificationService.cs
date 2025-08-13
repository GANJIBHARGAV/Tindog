using MailKit.Net.Smtp;
using MimeKit;
using SlaBreach.Infrastructure.Persistence;
using SlaBreach.Domain.Entities;

namespace SlaBreach.Infrastructure.Notifications;

public class NotificationService
{
    private readonly AppDbContext _db;
    private readonly IConfiguration _cfg;

    public NotificationService(AppDbContext db, IConfiguration cfg)
    {
        _db = db;
        _cfg = cfg;
    }

    public void SendEmail(IEnumerable<string> to, string subject, string body)
    {
        var message = new MimeMessage();
        message.From.Add(MailboxAddress.Parse(_cfg["Smtp:From"] ?? "alerts@example.local"));
        foreach (var t in to) message.To.Add(MailboxAddress.Parse(t));
        message.Subject = subject;
        message.Body = new TextPart("plain") { Text = body };

        string host = _cfg["Smtp:Host"] ?? "mailhog";
        int port = int.TryParse(_cfg["Smtp:Port"], out var p) ? p : 1025;

        string status = "success";
        string? error = null;
        try
        {
            using var client = new SmtpClient();
            client.Connect(host, port, MailKit.Security.SecureSocketOptions.StartTlsWhenAvailable);
            client.Send(message);
            client.Disconnect(true);
        }
        catch (Exception ex)
        {
            status = "failed";
            error = ex.Message;
        }
        _db.DeliveryLogs.Add(new DeliveryLog { Provider = "email", Status = status, ErrorMessage = error, Attempts = 1, MetaJson = System.Text.Json.JsonSerializer.Serialize(new { to, subject }) });
        _db.SaveChanges();
    }
}
