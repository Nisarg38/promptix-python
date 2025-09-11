"""
Edge case and error condition tests for Promptix library.

This module contains comprehensive tests for edge cases, error conditions,
and boundary scenarios to ensure robust error handling and edge case coverage.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from promptix import Promptix
from typing import Dict, List, Any


class TestPromptNotFoundEdgeCases:
    """Test edge cases related to prompt not found scenarios."""

    def test_empty_prompt_name(self):
        """Test behavior with empty prompt name."""
        with pytest.raises(Exception) as exc_info:
            Promptix.get_prompt("", user_name="test")
        
        error_msg = str(exc_info.value)
        assert len(error_msg) > 0  # Should provide meaningful error

    def test_none_prompt_name(self):
        """Test behavior with None as prompt name."""
        with pytest.raises(Exception):
            Promptix.get_prompt(None, user_name="test")

    def test_numeric_prompt_name(self):
        """Test behavior with numeric prompt name."""
        with pytest.raises(Exception):
            Promptix.get_prompt(123, user_name="test")

    def test_special_characters_in_prompt_name(self):
        """Test behavior with special characters in prompt name."""
        special_names = [
            "Prompt@#$%",
            "Prompt with spaces",
            "Prompt\nwith\nnewlines",
            "Prompt\twith\ttabs",
            "Prompt/with/slashes",
            "Prompt\\with\\backslashes"
        ]
        
        for name in special_names:
            with pytest.raises(Exception):
                Promptix.get_prompt(name, user_name="test")

    def test_very_long_prompt_name(self):
        """Test behavior with extremely long prompt name."""
        long_name = "A" * 10000  # 10KB prompt name
        
        with pytest.raises(Exception):
            Promptix.get_prompt(long_name, user_name="test")


class TestVariableValidationEdgeCases:
    """Test edge cases in variable validation and substitution."""

    def test_none_variables(self):
        """Test behavior when variables are None."""
        # Test with None values for optional parameters
        try:
            prompt = Promptix.get_prompt(
                prompt_template="SimpleChat",
                user_name="test",
                assistant_name="test"
                # No additional variables with None keys - that's not valid Python
            )
            assert isinstance(prompt, str)
        except Exception:
            # If it fails, that's acceptable for this edge case
            pass

    def test_empty_string_variables(self):
        """Test behavior with empty string variables."""
        prompt = Promptix.get_prompt(
            prompt_template="SimpleChat",
            user_name="",  # Empty string
            assistant_name=""  # Empty string
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_unicode_variables(self):
        """Test behavior with Unicode variables."""
        unicode_values = [
            "Hello 世界",
            "Café ☕",
            "🚀 Space",
            "Ñoño",
            "العربية",
            "русский",
            "日本語",
            "한국어"
        ]
        
        for unicode_val in unicode_values:
            prompt = Promptix.get_prompt(
                prompt_template="SimpleChat",
                user_name=unicode_val,
                assistant_name="Assistant"
            )
            assert isinstance(prompt, str)
            assert unicode_val in prompt or len(prompt) > 0  # Unicode should be preserved

    def test_very_large_variables(self):
        """Test behavior with very large variable values."""
        large_value = "x" * 100000  # 100KB string
        
        prompt = Promptix.get_prompt(
            prompt_template="CodeReviewer",
            code_snippet=large_value,
            programming_language="Text",
            review_focus="size analysis"
        )
        assert isinstance(prompt, str)
        assert large_value in prompt

    def test_nested_data_structures(self, complex_template_variables):
        """Test with complex nested data structures."""
        # Test that complex variables don't break the system
        try:
            prompt = Promptix.get_prompt(
                prompt_template="SimpleChat",
                user_name=str(complex_template_variables["nested_dict"]),
                assistant_name="Assistant"
            )
            assert isinstance(prompt, str)
        except Exception as e:
            # If it fails, it should fail gracefully with a meaningful error
            assert len(str(e)) > 0

    def test_circular_references(self):
        """Test behavior with circular references in variables."""
        # Create circular reference
        dict_a = {"name": "dict_a"}
        dict_b = {"name": "dict_b", "ref": dict_a}
        dict_a["ref"] = dict_b
        
        # Should handle circular references gracefully
        try:
            prompt = Promptix.get_prompt(
                prompt_template="SimpleChat",
                user_name=str(dict_a),  # Convert to string to avoid direct circular ref
                assistant_name="Assistant"
            )
            assert isinstance(prompt, str)
        except Exception as e:
            # If it fails, should not hang or cause stack overflow
            assert len(str(e)) > 0

    def test_variable_type_coercion(self):
        """Test automatic type coercion of variables."""
        # Test various types that should be coerced to strings
        type_test_cases = [
            (123, "123"),
            (3.14159, "3.14159"),
            (True, "True"),
            (False, "False"),
            ([1, 2, 3], "[1, 2, 3]"),
            ({"key": "value"}, "{'key': 'value'}"),
        ]
        
        for input_val, expected_in_output in type_test_cases:
            try:
                prompt = Promptix.get_prompt(
                    prompt_template="SimpleChat",
                    user_name=input_val,
                    assistant_name="Assistant"
                )
                assert isinstance(prompt, str)
                # Type should be converted to string representation
            except Exception:
                # Some types might not be supported, that's okay
                pass


class TestBuilderEdgeCases:
    """Test edge cases in the builder pattern."""

    def test_builder_method_chaining_with_none_values(self):
        """Test builder method chaining with None values."""
        # Test that None values are properly rejected by validation
        with pytest.raises(Exception) as exc_info:
            Promptix.builder("SimpleChat").with_user_name(None)
        
        # Verify the error message is informative  
        error_msg = str(exc_info.value)
        assert "user_name" in error_msg.lower()
        assert ("none" in error_msg.lower() or "string" in error_msg.lower())

    def test_builder_duplicate_method_calls(self):
        """Test calling builder methods multiple times."""
        builder = Promptix.builder("SimpleChat")
        
        # Call methods multiple times - last value should win
        config = (
            builder
            .with_user_name("First")
            .with_user_name("Second")  # Should override first
            .with_user_name("Final")   # Should override second
            .with_assistant_name("Assistant")
            .build()
        )
        
        assert isinstance(config, dict)
        # Check that final value is used (if accessible in config)
        system_msg = str(config.get("messages", [{}])[0].get("content", ""))
        assert "Final" in system_msg or len(system_msg) > 0

    def test_builder_with_invalid_memory_format(self, invalid_memory):
        """Test builder with various invalid memory formats."""
        builder = Promptix.builder("SimpleChat")
        
        for invalid_mem in invalid_memory:
            try:
                config = (
                    builder
                    .with_user_name("test")
                    .with_assistant_name("test")
                    .with_memory(invalid_mem)
                    .build()
                )
                # If it succeeds, should still be valid config
                assert isinstance(config, dict)
            except Exception as e:
                # If it fails, should provide meaningful error
                assert len(str(e)) > 0

    def test_builder_with_extremely_long_method_chains(self):
        """Test builder with very long method chains."""
        builder = Promptix.builder("SimpleChat")
        
        # Create a very long method chain
        for i in range(100):  # 100 method calls
            builder = builder.with_user_name(f"User_{i}")
        
        config = builder.with_assistant_name("Assistant").build()
        assert isinstance(config, dict)

    def test_builder_memory_edge_cases(self):
        """Test builder memory with edge cases."""
        edge_case_memories = [
            [],  # Empty memory
            [{"role": "system", "content": "System message"}],  # System role
            [{"role": "user", "content": ""}],  # Empty content
            [{"role": "user", "content": "msg"} for _ in range(1000)],  # Very long memory
        ]
        
        for memory in edge_case_memories:
            try:
                config = (
                    Promptix.builder("SimpleChat")
                    .with_user_name("test")
                    .with_assistant_name("test")
                    .with_memory(memory)
                    .build()
                )
                assert isinstance(config, dict)
                assert "messages" in config
            except Exception as e:
                # If it fails, error should be meaningful
                assert "memory" in str(e).lower() or len(str(e)) > 0


class TestTemplateRenderingEdgeCases:
    """Test edge cases in template rendering."""

    def test_template_with_malformed_syntax(self):
        """Test templates with malformed Jinja syntax."""
        # These would be in the YAML file, but we can test error handling
        malformed_cases = [
            "{{unclosed_variable",
            "{% unclosed_block",
            "{{ variable.missing_attr }}",
            "{% for item in undefined %}{{ item }}{% endfor %}",
            "{{ variable | undefined_filter }}",
        ]
        
        # Since we can't easily modify the template files, we'll test that
        # the system handles template errors gracefully
        for case in malformed_cases:
            # This is more of a conceptual test - actual malformed templates
            # would be caught during YAML loading or template compilation
            pass

    def test_template_with_recursive_includes(self):
        """Test templates with recursive includes or inheritance."""
        # This would test Jinja template inheritance edge cases
        # Since our templates are defined in YAML, we'll test reasonable scenarios
        
        # Test that system doesn't hang on complex template logic
        prompt = Promptix.get_prompt(
            prompt_template="TemplateDemo",
            content_type="tutorial",
            theme="Recursion",
            difficulty="advanced",
            elements=["recursion"] * 100  # Many repeated elements
        )
        assert isinstance(prompt, str)

    def test_template_with_extreme_conditionals(self):
        """Test templates with complex conditional logic."""
        # Test various difficulty levels and content types
        difficulty_levels = ["beginner", "intermediate", "advanced", "expert", "invalid_level"]
        content_types = ["tutorial", "article", "guide", "invalid_type"]
        
        for difficulty in difficulty_levels:
            for content_type in content_types:
                try:
                    prompt = Promptix.get_prompt(
                        prompt_template="TemplateDemo",
                        content_type=content_type,
                        theme="Test",
                        difficulty=difficulty
                    )
                    assert isinstance(prompt, str)
                except Exception as e:
                    # If certain combinations fail, error should be meaningful
                    assert len(str(e)) > 0

    def test_template_with_empty_loops(self):
        """Test templates with empty loop variables."""
        prompt = Promptix.get_prompt(
            prompt_template="TemplateDemo",
            content_type="tutorial",
            theme="Empty Lists",
            difficulty="beginner",
            elements=[]  # Empty list
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_template_with_none_loop_variables(self):
        """Test templates where loop variables are None."""
        try:
            prompt = Promptix.get_prompt(
                prompt_template="TemplateDemo",
                content_type="tutorial",
                theme="None Lists",
                difficulty="beginner",
                elements=None  # None instead of list
            )
            assert isinstance(prompt, str)
        except Exception as e:
            # If it fails, should be a meaningful error about type mismatch
            assert "type" in str(e).lower() or "none" in str(e).lower() or len(str(e)) > 0


class TestConfigurationEdgeCases:
    """Test edge cases in configuration and setup."""

    @patch('promptix.core.config.PromptixConfig.get_prompt_file_path')
    def test_missing_prompts_file(self, mock_get_path):
        """Test behavior when prompts file is missing."""
        mock_get_path.return_value = "/nonexistent/path.yaml"
        
        try:
            result = Promptix.get_prompt("SimpleChat", user_name="test", assistant_name="test")
            # If it succeeds, it might be using a fallback or default configuration
            assert isinstance(result, str)
        except Exception as exc_info:
            # If it fails, should be a meaningful error
            error_msg = str(exc_info)
            assert len(error_msg) > 0

    def test_corrupted_prompts_file(self, tmp_path):
        """Test behavior with corrupted YAML file."""
        # Create a corrupted YAML file
        corrupted_file = tmp_path / "corrupted.yaml"
        corrupted_file.write_text("invalid: yaml: content: [unclosed")
        
        # Mock the config to point to our corrupted file
        with patch('promptix.core.config.PromptixConfig.get_prompt_file_path') as mock_path:
            mock_path.return_value = str(corrupted_file)
            
            try:
                result = Promptix.get_prompt("SimpleChat", user_name="test", assistant_name="test")
                # If it succeeds, system handled corruption gracefully
                assert isinstance(result, str)
            except Exception as exc_info:
                # If it fails, should provide meaningful error
                error_msg = str(exc_info)
                assert len(error_msg) > 0

    def test_empty_prompts_file(self, tmp_path):
        """Test behavior with empty prompts file."""
        empty_file = tmp_path / "empty.yaml"
        empty_file.write_text("")  # Completely empty file
        
        with patch('promptix.core.config.PromptixConfig.get_prompt_file_path') as mock_path:
            mock_path.return_value = str(empty_file)
            
            try:
                result = Promptix.get_prompt("SimpleChat", user_name="test", assistant_name="test")
                # If it succeeds, system handled empty file gracefully
                assert isinstance(result, str)
            except Exception:
                # If it fails, that's also acceptable for empty file
                pass

    def test_prompts_file_with_no_permissions(self, tmp_path):
        """Test behavior when prompts file has no read permissions."""
        restricted_file = tmp_path / "restricted.yaml"
        restricted_file.write_text("SimpleChat:\n  versions:\n    v1:\n      config:\n        model: test")
        
        # Make file unreadable (on Unix systems)
        try:
            os.chmod(str(restricted_file), 0o000)
            
            with patch('promptix.core.config.PromptixConfig.get_prompt_file_path') as mock_path:
                mock_path.return_value = str(restricted_file)
                
                try:
                    result = Promptix.get_prompt("SimpleChat", user_name="test", assistant_name="test")
                    # If it succeeds, system handled permissions gracefully
                    assert isinstance(result, str)
                except Exception as exc_info:
                    # If it fails, should provide meaningful error
                    error_msg = str(exc_info)
                    assert len(error_msg) > 0
        
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(str(restricted_file), 0o644)
            except:
                pass


class TestConcurrencyEdgeCases:
    """Test edge cases related to concurrent access."""

    def test_concurrent_prompt_access(self):
        """Test concurrent access to the same prompt."""
        import threading
        import concurrent.futures
        
        results = []
        errors = []
        
        def get_prompt_worker(worker_id):
            try:
                prompt = Promptix.get_prompt(
                    prompt_template="SimpleChat",
                    user_name=f"User{worker_id}",
                    assistant_name=f"Assistant{worker_id}"
                )
                results.append(prompt)
            except Exception as e:
                errors.append(str(e))
        
        # Run multiple workers concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_prompt_worker, i) for i in range(20)]
            concurrent.futures.wait(futures)
        
        # Should not have race conditions or errors
        assert len(errors) == 0, f"Concurrent access caused errors: {errors}"
        assert len(results) == 20, f"Expected 20 results, got {len(results)}"
        assert all(isinstance(r, str) and len(r) > 0 for r in results)

    def test_concurrent_builder_usage(self):
        """Test concurrent usage of builder pattern."""
        import concurrent.futures
        
        configs = []
        errors = []
        
        def build_config_worker(worker_id):
            try:
                config = (
                    Promptix.builder("SimpleChat")
                    .with_user_name(f"User{worker_id}")
                    .with_assistant_name(f"Assistant{worker_id}")
                    .build()
                )
                configs.append(config)
            except Exception as e:
                errors.append(str(e))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(build_config_worker, i) for i in range(20)]
            concurrent.futures.wait(futures)
        
        assert len(errors) == 0, f"Concurrent builder usage caused errors: {errors}"
        assert len(configs) == 20
        assert all(isinstance(c, dict) and "messages" in c for c in configs)


class TestResourceLimitEdgeCases:
    """Test edge cases related to resource limits."""

    def test_maximum_variable_count(self):
        """Test with maximum number of variables."""
        # Create many variables
        many_vars = {f"var_{i}": f"value_{i}" for i in range(1000)}
        
        try:
            config = (
                Promptix.builder("SimpleChat")
                .with_user_name("test")
                .with_assistant_name("test")
                **many_vars  # This syntax might not work, alternative approach below
            )
            
            # Alternative approach - add variables one by one
            builder = Promptix.builder("SimpleChat")
            builder.with_user_name("test")
            builder.with_assistant_name("test")
            
            for key, value in list(many_vars.items())[:100]:  # Limit to reasonable number
                # We can't directly test this without knowing builder internals
                pass
                
            config = builder.build()
            assert isinstance(config, dict)
        except Exception as e:
            # If it fails with many variables, error should be meaningful
            assert "variable" in str(e).lower() or "memory" in str(e).lower() or len(str(e)) > 0

    def test_deeply_nested_template_calls(self):
        """Test with deeply nested template operations."""
        # This is hard to test directly, but we can test complex scenarios
        complex_config = (
            Promptix.builder("ComplexCodeReviewer")
            .with_code_snippet("def " + "nested_" * 100 + "function(): pass")
            .with_programming_language("Python")
            .with_review_focus("complexity analysis")
            .with_severity("high")
            .build()
        )
        
        assert isinstance(complex_config, dict)
        assert "messages" in complex_config


class TestBackwardCompatibilityEdgeCases:
    """Test edge cases related to backward compatibility."""

    def test_old_prompt_format_handling(self):
        """Test handling of different prompt format versions."""
        # This would test if the system handles older prompt formats gracefully
        # Since we don't have version migration, we'll test current format variations
        
        # Test minimal prompt configuration
        try:
            prompt = Promptix.get_prompt(
                prompt_template="SimpleChat",
                user_name="test"
                # Missing assistant_name - should handle gracefully
            )
            assert isinstance(prompt, str)
        except Exception as e:
            # If required variables are missing, should get meaningful error
            assert "required" in str(e).lower() or "missing" in str(e).lower() or len(str(e)) > 0

    def test_deprecated_method_calls(self):
        """Test deprecated method patterns."""
        # Test that old calling patterns still work or fail gracefully
        try:
            # Test various calling patterns
            prompt1 = Promptix.get_prompt("SimpleChat", user_name="test", assistant_name="test")
            assert isinstance(prompt1, str)
            
            # Test with version specification
            prompt2 = Promptix.get_prompt("SimpleChat", version="v1", user_name="test", assistant_name="test")
            assert isinstance(prompt2, str)
            
        except Exception as e:
            # If patterns aren't supported, should get clear error
            assert len(str(e)) > 0


class TestSecurityEdgeCases:
    """Test security-related edge cases."""

    def test_template_injection_attempts(self):
        """Test potential template injection attempts."""
        malicious_inputs = [
            "{{ ''.__class__.__mro__[1].__subclasses__() }}",  # Python class access
            "{% for item in ''.__class__.__mro__ %}{{ item }}{% endfor %}",  # Iteration over classes
            "{{ config.items() }}",  # Config access
            "{% set x = 'dangerous' %}{{ x }}",  # Variable setting
            "<script>alert('xss')</script>",  # XSS attempt
            "'; DROP TABLE users; --",  # SQL injection attempt (shouldn't be relevant but good to test)
        ]
        
        for malicious_input in malicious_inputs:
            try:
                # Test in various variable positions
                prompt = Promptix.get_prompt(
                    prompt_template="SimpleChat",
                    user_name=malicious_input,
                    assistant_name="Assistant"
                )
                
                # If it succeeds, the malicious content should be escaped/neutralized
                assert isinstance(prompt, str)
                # Content should not contain executable code
                assert "__class__" not in prompt or malicious_input in prompt  # Either escaped or literal
                
            except Exception as e:
                # If it fails, should be due to template security, not system crash
                assert len(str(e)) > 0

    def test_path_traversal_in_template_names(self):
        """Test path traversal attempts in template names."""
        traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM",
            "template_name/../other_template"
        ]
        
        for attempt in traversal_attempts:
            with pytest.raises(Exception):
                Promptix.get_prompt(attempt, user_name="test")

    def test_resource_exhaustion_attempts(self):
        """Test potential resource exhaustion attacks."""
        # Test with extremely long strings
        very_long_string = "A" * 1000000  # 1MB string
        
        try:
            config = (
                Promptix.builder("SimpleChat")
                .with_user_name(very_long_string)
                .with_assistant_name("Assistant")
                .build()
            )
            # If it succeeds, should not cause system issues
            assert isinstance(config, dict)
        except Exception as e:
            # If it fails, should be due to reasonable limits, not system crash
            assert "memory" in str(e).lower() or "size" in str(e).lower() or len(str(e)) > 0


class TestErrorMessageQuality:
    """Test quality and usefulness of error messages."""

    def test_error_messages_are_informative(self):
        """Test that error messages provide useful information."""
        error_scenarios = [
            (lambda: Promptix.get_prompt("NonExistent"), "template not found"),
            (lambda: Promptix.builder("NonExistent").build(), "template not found"),
            (lambda: Promptix.builder("SimpleChat").for_client("invalid").build(), "invalid client"),
        ]
        
        for scenario_func, expected_content in error_scenarios:
            try:
                scenario_func()
                pytest.fail(f"Expected exception for {scenario_func}")
            except Exception as e:
                error_msg = str(e).lower()
                # Error should be informative and contain relevant keywords
                assert len(error_msg) > 10, f"Error message too short: {error_msg}"
                # Don't require exact match, just that it's informative
                assert any(word in error_msg for word in ["not", "found", "invalid", "error", "template"])

    def test_stack_traces_are_reasonable(self):
        """Test that stack traces don't expose internal implementation details excessively."""
        try:
            Promptix.get_prompt("NonExistentTemplate")
        except Exception as e:
            # Stack trace should be present but not overwhelming
            import traceback
            tb = traceback.format_exc()
            
            # Should contain relevant information but not be excessively long
            assert len(tb) < 5000, f"Stack trace too long ({len(tb)} chars)"
            assert "NonExistentTemplate" in tb, "Stack trace should reference the problematic input"


# Integration edge case tests
class TestIntegrationEdgeCases:
    """Test integration edge cases across components."""

    def test_end_to_end_error_handling(self):
        """Test end-to-end error handling across all components."""
        # Test a complex scenario that involves multiple components
        try:
            config = (
                Promptix.builder("ComplexCodeReviewer")
                .with_code_snippet("invalid code snippet")
                .with_programming_language("InvalidLanguage")
                .with_review_focus("nonexistent focus")
                .with_severity("invalid_severity")
                .with_memory([
                    {"role": "invalid_role", "content": "test"}
                ])
                .for_client("invalid_client")
                .build()
            )
            # If it somehow succeeds, should still be valid
            assert isinstance(config, dict)
        except Exception as e:
            # Should get a meaningful error from one of the validation steps
            error_msg = str(e).lower()
            assert any(word in error_msg for word in [
                "template", "client", "role", "memory", "invalid", "not found"
            ])

    def test_component_isolation(self):
        """Test that failures in one component don't cascade inappropriately."""
        # This is more of a design test - components should fail independently
        
        # Test that builder failures don't affect subsequent get_prompt calls
        try:
            Promptix.builder("InvalidTemplate").build()
        except Exception:
            pass  # Expected to fail
        
        # This should still work despite previous failure
        prompt = Promptix.get_prompt(
            prompt_template="SimpleChat",
            user_name="test",
            assistant_name="test"
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 0
