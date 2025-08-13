using Microsoft.AspNetCore.Mvc;

namespace SlaBreach.Api.Controllers;

[ApiController]
[Route("api")]
public class HealthController : ControllerBase
{
    [HttpGet("health")]
    public IActionResult Health() => Ok(new { status = "ok" });

    [HttpGet("version")]
    public IActionResult Version() => Ok(new { version = "0.1.0" });
}
