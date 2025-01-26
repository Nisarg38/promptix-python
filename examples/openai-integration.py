from promptix import Promptix
import openai

def main():

    client = openai.OpenAI()

    # New prepare_model_config example that returns model config
    print("Using prepare_model_config:")
    memory = [
        {"role": "user", "content": "I'm having trouble resetting my password"},
        {"role": "assistant", "content": "I understand you're having password reset issues. Could you tell me what happens when you try?"}
    ]
    
    
    model_config = Promptix.prepare_model_config(
        prompt_template="CustomerSupport",
        user_name="John Doe",
        issue_type="password reset",
        technical_level="intermediate",
        interaction_history="2 previous tickets about 2FA setup",
        product_version="2.1.0",
        issue_description="User is unable to reset their password after multiple attempts",
        custom_data={"product_version": "2.1.0", "subscription_tier": "standard"},
        memory=memory,
    )

    response = client.chat.completions.create(**model_config)
    
    
    print("Model Config:", model_config)
    print("\nResponse:", response)

if __name__ == "__main__":
    main() 