# Bring your own API key

You can add your own API keys so Cursor uses your preferred AI models. This lets you send unlimited AI messages at your own cost through providers like OpenAI, Anthropic, or Google.

## How do I add an API key?

1. Open **Cursor Settings** > **Models**
2. Find the provider you want (OpenAI, Anthropic, Google, Azure, or AWS Bedrock)
3. Paste your API key into the text field
4. Click **Save**

Cursor now uses your key for that provider's models. They appear in the model picker. If a key is invalid or rejected by the provider, requests using that provider fail until you update or remove the key.

## What providers are supported?

- **OpenAI**: Standard, non-reasoning chat models. The model picker shows which OpenAI models are available.
- **Anthropic**: All Claude models available through the Anthropic API.
- **Google**: Gemini models available through the Google AI API.
- **Azure OpenAI**: Models deployed in your Azure OpenAI Service instance.
- **AWS Bedrock**: Use AWS access keys and secret keys in the IDE, or configure IAM roles through the [Cursor dashboard](https://cursor.com/dashboard). Works with models available in your Bedrock configuration. See the [AWS Bedrock setup guide](https://cursor.com/docs/customizing/aws-bedrock.md) for detailed instructions.

Custom API keys only work with chat models. Tab completion continues using Cursor's built-in models.

## Does Cursor's Zero Data Retention policy apply when using my own API keys?

No. Cursor's [Zero Data Retention policy](https://cursor.com/docs/account/teams/dashboard.md#privacy-settings) does not apply when you use your own API keys. Your data handling follows the privacy policy of your chosen provider (OpenAI, Anthropic, Google, Azure, or AWS).

If your team relies on Zero Data Retention, use Cursor's built-in models instead.

## Will my API key be stored or leave my device?

Your API key is not stored on our servers. It is sent to our backend with every request because all requests are routed through Cursor's servers for final prompt building. The key is transmitted over encrypted connections and is not persisted after the request completes.

## Related

- [AWS Bedrock setup guide](https://cursor.com/docs/customizing/aws-bedrock.md)
- [Available models](https://cursor.com/help/models-and-usage/available-models.md)
- [Privacy and data](https://cursor.com/help/security-and-privacy/privacy.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
