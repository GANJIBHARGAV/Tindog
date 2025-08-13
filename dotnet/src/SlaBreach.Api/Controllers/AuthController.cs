using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using SlaBreach.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;
using BCrypt.Net;

namespace SlaBreach.Api.Controllers;

[ApiController]
[Route("api/auth")]
public class AuthController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly IConfiguration _cfg;
    public AuthController(AppDbContext db, IConfiguration cfg) { _db = db; _cfg = cfg; }

    public record LoginRequest(string Email, string Password);
    public record TokenResponse(string AccessToken, string TokenType = "bearer");

    [HttpPost("login")]
    public async Task<ActionResult<TokenResponse>> Login([FromBody] LoginRequest req)
    {
        var user = await _db.Users.FirstOrDefaultAsync(u => u.Email == req.Email);
        if (user is null) return BadRequest(new { detail = "Invalid credentials" });
        if (!BCrypt.Net.BCrypt.Verify(req.Password, user.HashedPassword)) return BadRequest(new { detail = "Invalid credentials" });

        var jwtSection = _cfg.GetSection("Jwt");
        var secret = jwtSection["Secret"]!;
        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secret));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);
        var token = new JwtSecurityToken(
            issuer: jwtSection["Issuer"],
            audience: jwtSection["Audience"],
            claims: new[] { new Claim(JwtRegisteredClaimNames.Sub, user.Email), new Claim("role", user.Role) },
            expires: DateTime.UtcNow.AddHours(12),
            signingCredentials: creds
        );
        var jwt = new JwtSecurityTokenHandler().WriteToken(token);
        return Ok(new TokenResponse(jwt));
    }
}
