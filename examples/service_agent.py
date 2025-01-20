from promptix import Promptix

def main():
    print("Service Agent Examples:\n")
    
    # Example 1: New user, phone call, with transportation
    print("\nExample 1: New user on phone call with transportation needs")
    print("-" * 50)
    prompt1 = Promptix.get_prompt(
        prompt_template="ServiceAgent",
        new_user=True,
        communication_type="phone",
        transportation_type=True,
        scheduling_required=False
    )
    print(prompt1)
    
    # Example 2: Returning user, SMS, with scheduling
    print("\nExample 2: Returning user via SMS with scheduling needs")
    print("-" * 50)
    prompt2 = Promptix.get_prompt(
        prompt_template="ServiceAgent",
        new_user=False,
        communication_type="sms",
        transportation_type=False,
        scheduling_required=True
    )
    print(prompt2)
    
    # Example 3: Simple one-liner with minimal options
    print("\nExample 3: Simple chat conversation")
    print("-" * 50)
    prompt3 = Promptix.get_prompt(
        prompt_template="ServiceAgent",
        communication_type="chat"  # Only providing the required field
    )
    print(prompt3)
    
    # Example 4: All services enabled
    print("\nExample 4: Full service request")
    print("-" * 50)
    prompt4 = Promptix.get_prompt(
        prompt_template="ServiceAgent",
        new_user=True,
        communication_type="phone",
        transportation_type=True,
        scheduling_required=True
    )
    print(prompt4)

if __name__ == "__main__":
    main() 