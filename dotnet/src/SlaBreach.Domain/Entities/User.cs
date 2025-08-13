using System;

namespace SlaBreach.Domain.Entities;

public enum UserRole { Admin, Manager, Viewer }

public class User
{
    public int Id { get; set; }
    public string Email { get; set; } = string.Empty;
    public string HashedPassword { get; set; } = string.Empty;
    public string Role { get; set; } = UserRole.Viewer.ToString();
    public bool IsActive { get; set; } = true;
    public DateTimeOffset CreatedAt { get; set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; set; } = DateTimeOffset.UtcNow;
}