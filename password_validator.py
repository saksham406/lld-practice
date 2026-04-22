import re
from typing import List
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

# 1. DTO for the Result
# Using a dataclass for clean data encapsulation
@dataclass
class ValidationResult:
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)

    def add_error(self, error: str) -> None:
        self.is_valid = False
        self.errors.append(error)

# 2. The Strategy Interface
# Defines the contract for all rules
class PasswordRule(ABC):
    @abstractmethod
    def validate(self, password: str) -> ValidationResult:
        pass

# 3. Concrete Strategies (Adhering to Single Responsibility Principle)
class MinLengthRule(PasswordRule):
    def __init__(self, min_length: int = 8):
        self.min_length = min_length

    def validate(self, password: str) -> ValidationResult:
        result = ValidationResult()
        if not password or len(password) < self.min_length:
            result.add_error(f"Password must be at least {self.min_length} characters long.")
        return result

class UppercaseRule(PasswordRule):
    def validate(self, password: str) -> ValidationResult:
        result = ValidationResult()
        if not password or not re.search(r'[A-Z]', password):
            result.add_error("Password must contain at least one uppercase letter.")
        return result

# 4. The Context / Policy Manager
class PasswordValidator:
    def __init__(self):
        self.rules: List[PasswordRule] = []

    def add_rule(self, rule: PasswordRule) -> 'PasswordValidator':
        """Adds a rule and returns self for fluent chaining."""
        self.rules.append(rule)
        return self

    def validate(self, password: str) -> ValidationResult:
        final_result = ValidationResult()

        for rule in self.rules:
            rule_result = rule.validate(password)
            if not rule_result.is_valid:
                # Aggregate all errors for comprehensive user feedback
                final_result.is_valid = False
                final_result.errors.extend(rule_result.errors)

        return final_result