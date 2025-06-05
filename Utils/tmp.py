# Extract numbers from the comment block and compute their sum
def process_numbers_from_comment():
    # List of numbers extracted from the comment
    numbers = [6, 6, 6, 6, 3, 6, 6, 6, 18, 24, 18, 6, 6, 6, 3, 3, 3, 6, 6]
    
    # Compute the sum
    total_sum = sum(numbers)
    
    # Return the result
    return total_sum

# Example usage
result = process_numbers_from_comment()
print("Sum of numbers:", result)