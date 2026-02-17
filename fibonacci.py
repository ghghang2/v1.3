#!/usr/bin/env python3
"""
Simple Fibonacci number calculator.
"""

def fibonacci_iterative(n: int) -> int:
    """
    Calculate the nth Fibonacci number using iterative method.
    
    Args:
        n: Position in Fibonacci sequence (0-indexed)
        
    Returns:
        The nth Fibonacci number
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def fibonacci_recursive(n: int) -> int:
    """
    Calculate the nth Fibonacci number using recursion.
    
    Warning: This is inefficient for large n (exponential time complexity).
    
    Args:
        n: Position in Fibonacci sequence (0-indexed)
        
    Returns:
        The nth Fibonacci number
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    
    if n <= 1:
        return n
    
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


def fibonacci_memoized(n: int, memo: dict = None) -> int:
    """
    Calculate the nth Fibonacci number using memoization (dynamic programming).
    
    Args:
        n: Position in Fibonacci sequence (0-indexed)
        memo: Dictionary for memoization (optional)
        
    Returns:
        The nth Fibonacci number
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    
    if memo is None:
        memo = {}
    
    if n in memo:
        return memo[n]
    
    if n <= 1:
        result = n
    else:
        result = fibonacci_memoized(n - 1, memo) + fibonacci_memoized(n - 2, memo)
    
    memo[n] = result
    return result


def generate_fibonacci_sequence(length: int) -> list[int]:
    """
    Generate a Fibonacci sequence of specified length.
    
    Args:
        length: Number of Fibonacci numbers to generate
        
    Returns:
        List of Fibonacci numbers
        
    Raises:
        ValueError: If length is negative
    """
    if length < 0:
        raise ValueError("length must be non-negative")
    
    if length == 0:
        return []
    
    sequence = [0]
    if length == 1:
        return sequence
    
    sequence.append(1)
    for i in range(2, length):
        sequence.append(sequence[i-1] + sequence[i-2])
    
    return sequence


def main():
    """Demonstrate the Fibonacci functions."""
    print("Fibonacci Sequence Examples:")
    print("-" * 40)
    
    # Generate first 10 Fibonacci numbers
    n = 10
    sequence = generate_fibonacci_sequence(n)
    print(f"First {n} Fibonacci numbers: {sequence}")
    
    # Compare different methods
    test_values = [0, 1, 5, 10, 20]
    print("\nComparison of different methods:")
    for value in test_values:
        iter_result = fibonacci_iterative(value)
        memo_result = fibonacci_memoized(value)
        print(f"F({value}) = {iter_result} (iterative)")
        print(f"F({value}) = {memo_result} (memoized)")
        
        if value <= 15:  # Avoid recursion depth issues
            rec_result = fibonacci_recursive(value)
            print(f"F({value}) = {rec_result} (recursive)")
        print()
    
    print("-" * 40)
    print(f"F(20) using iterative method: {fibonacci_iterative(20)}")
    print(f"F(30) using memoized method: {fibonacci_memoized(30)}")


if __name__ == "__main__":
    main()