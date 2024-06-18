using Azure.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Connectors.OpenAI;
using Microsoft.SemanticKernel.Plugins.Core.CodeInterpreter;

#pragma warning disable SKEXP0050


var builder = WebApplication.CreateBuilder(args);

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddHttpClient();
builder.Services.AddLogging(b =>
{
    b.AddConsole();
});

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI();

app.UseHttpsRedirection();

string? cachedToken = null;
async Task<string> TokenProvider()
{
    if (cachedToken is null)
    {
        string resource = "https://acasessions.io/.default";
        var credential = new DefaultAzureCredential();
        var accessToken = await credential.GetTokenAsync(new Azure.Core.TokenRequestContext([resource])).ConfigureAwait(false);
        cachedToken = accessToken.Token;
    }

    return cachedToken;
}

app.MapGet("/chat", async ([FromQuery] string message, IHttpClientFactory httpClientFactory, ILoggerFactory loggerFactory) =>
{
    var sessionId = Guid.NewGuid().ToString();
    var poolManagementEndpoint = new Uri(Environment.GetEnvironmentVariable("POOL_MANAGEMENT_ENDPOINT")!);
    var azureOpenAIEndpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")!;
    var settings = new SessionsPythonSettings(
            sessionId: sessionId,
            endpoint: poolManagementEndpoint);

    var builder =
        Kernel.CreateBuilder()
        .AddAzureOpenAIChatCompletion("gpt-35-turbo", azureOpenAIEndpoint, new DefaultAzureCredential());

    builder.Services
        .AddLogging(loggingBuilder => loggingBuilder.AddConsole().SetMinimumLevel(LogLevel.Information))
        .AddSingleton((sp)
            => new SessionsPythonPlugin(
                settings,
                httpClientFactory,
                TokenProvider,
                loggerFactory));

    var kernel = builder.Build();
    kernel.Plugins.AddFromObject(kernel.GetRequiredService<SessionsPythonPlugin>());

    var chatCompletion = kernel.GetRequiredService<IChatCompletionService>();

    var chatHistory = new ChatHistory();
    chatHistory.AddUserMessage(message);

    var chatCompletionService = kernel.GetRequiredService<IChatCompletionService>();

    var response = await chatCompletionService.GetChatMessageContentsAsync(chatHistory,
        new OpenAIPromptExecutionSettings { ToolCallBehavior = ToolCallBehavior.AutoInvokeKernelFunctions },
        kernel).ConfigureAwait(false);

    return new
    {
        output = response.FirstOrDefault()?.Items.FirstOrDefault()?.ToString()
    };
})
.WithName("Chat")
.WithOpenApi();

app.MapGet("/docs", () => Results.Redirect("/swagger")).ExcludeFromDescription();

app.Run();
