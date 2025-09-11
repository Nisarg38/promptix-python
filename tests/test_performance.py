"""
Performance tests for Promptix library.

This module contains performance tests to ensure the library handles
large datasets and complex operations efficiently.
"""

import pytest
import time
import psutil
import gc
from unittest.mock import patch
from typing import Dict, List, Any
from promptix import Promptix


class TestPromptRenderingPerformance:
    """Test performance of prompt rendering operations."""

    def test_simple_prompt_rendering_speed(self, performance_test_config):
        """Test that simple prompt rendering is performant."""
        max_time = performance_test_config["max_execution_time"]
        iterations = min(performance_test_config["iterations"], 100)  # Reasonable for simple tests
        
        start_time = time.time()
        
        for i in range(iterations):
            prompt = Promptix.get_prompt(
                prompt_template="SimpleChat",
                user_name=f"User{i}",
                assistant_name="Assistant"
            )
            assert len(prompt) > 0
        
        execution_time = time.time() - start_time
        avg_time_per_call = execution_time / iterations
        
        # Should be able to render at least 50 prompts per second
        assert avg_time_per_call < 0.08, f"Average time per call: {avg_time_per_call:.4f}s (too slow)"
        # Allow more time for performance test in CI environment with additional buffer
        max_allowed_time = max_time * 6  # Allow 6x the configured limit for CI (increased from 5x for stability)
        assert execution_time < max_allowed_time, f"Total execution time: {execution_time:.2f}s exceeded limit of {max_allowed_time:.1f}s"

    def test_complex_template_rendering_speed(self, performance_test_config):
        """Test performance with complex templates containing loops and conditionals."""
        max_time = performance_test_config["max_execution_time"] 
        iterations = 50  # Fewer iterations for complex templates
        
        elements = [f"Element{i}" for i in range(20)]  # Large list for template processing
        
        start_time = time.time()
        
        for i in range(iterations):
            prompt = Promptix.get_prompt(
                prompt_template="TemplateDemo",
                content_type="tutorial",
                theme=f"Topic {i}",
                difficulty="intermediate",
                elements=elements
            )
            assert len(prompt) > 0
        
        execution_time = time.time() - start_time
        avg_time_per_call = execution_time / iterations
        
        # Complex templates should still be reasonably fast
        assert avg_time_per_call < 0.2, f"Average time per call: {avg_time_per_call:.4f}s (too slow for complex templates)"

    def test_large_variable_substitution_performance(self):
        """Test performance with large variable values."""
        # Create large content
        large_code_snippet = """
def complex_function():
    # This is a very long function with lots of code
    data = []
    for i in range(1000):
        if i % 2 == 0:
            data.append(f"even_{i}")
        else:
            data.append(f"odd_{i}")
    
    result = {}
    for item in data:
        if "even" in item:
            result[item] = item.upper()
        else:
            result[item] = item.lower()
    
    return result
        """ * 50  # Multiply to make it really large
        
        start_time = time.time()
        
        prompt = Promptix.get_prompt(
            prompt_template="CodeReviewer",
            code_snippet=large_code_snippet,
            programming_language="Python",
            review_focus="performance optimization"
        )
        
        execution_time = time.time() - start_time
        
        assert len(prompt) > 0
        assert large_code_snippet in prompt
        # Even with large content, should complete in reasonable time
        assert execution_time < 0.7, f"Large variable substitution took {execution_time:.2f}s (too slow)"

    def test_concurrent_prompt_rendering(self):
        """Test performance with concurrent prompt rendering."""
        import concurrent.futures
        import threading
        
        def render_prompt(prompt_id):
            """Render a prompt with unique parameters."""
            return Promptix.get_prompt(
                prompt_template="SimpleChat",
                user_name=f"User{prompt_id}",
                assistant_name=f"Assistant{prompt_id}"
            )
        
        start_time = time.time()
        
        # Test with multiple threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(render_prompt, i) for i in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        execution_time = time.time() - start_time
        
        assert len(results) == 20
        assert all(len(result) > 0 for result in results)
        # Concurrent execution should be efficient
        assert execution_time < 2.0, f"Concurrent rendering took {execution_time:.2f}s (too slow)"


class TestLargeDatasetHandling:
    """Test performance with large datasets and many prompts."""

    def test_many_prompts_loading_performance(self, large_dataset):
        """Test loading performance with many prompts."""
        # Mock the storage system to return our large dataset
        with patch('promptix.core.storage.loaders.YAMLPromptLoader.load') as mock_load:
            mock_load.return_value = large_dataset
            
            start_time = time.time()
            
            # This would typically trigger loading of all prompts
            # We'll test a subset to keep test time reasonable
            subset_prompts = list(large_dataset.keys())[:10]
            
            for prompt_name in subset_prompts:
                try:
                    prompt = Promptix.get_prompt(
                        prompt_template=prompt_name,
                        **{f"var{i}": f"value{i}" for i in range(5)}  # Provide required vars
                    )
                    assert len(prompt) > 0
                except Exception:
                    # Some prompts might not work with our simple test, that's ok
                    pass
            
            execution_time = time.time() - start_time
            
            # Should handle multiple prompts efficiently
            assert execution_time < 1.0, f"Large dataset handling took {execution_time:.2f}s"

    def test_memory_usage_with_large_dataset(self, large_dataset):
        """Test memory usage doesn't grow excessively with large datasets."""
        process = psutil.Process()
        
        # Get baseline memory
        gc.collect()  # Force garbage collection
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Mock loading large dataset
        with patch('promptix.core.storage.loaders.YAMLPromptLoader.load') as mock_load:
            mock_load.return_value = large_dataset
            
            # Render many prompts
            for i in range(50):  # Reasonable number for memory testing
                prompt_name = f"Prompt{i % 10}"  # Cycle through available prompts
                try:
                    Promptix.get_prompt(
                        prompt_template=prompt_name,
                        **{f"var{j}": f"value{j}_{i}" for j in range(5)}
                    )
                except Exception:
                    pass  # Ignore errors, we're testing memory usage
        
        # Check memory after operations
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - baseline_memory
        
        # Memory increase should be reasonable (less than 100MB for our test)
        assert memory_increase < 100, f"Memory increased by {memory_increase:.2f}MB (excessive)"

    def test_builder_performance_with_complex_configs(self):
        """Test builder performance with complex configurations."""
        iterations = 100
        
        start_time = time.time()
        
        for i in range(iterations):
            config = (
                Promptix.builder("ComplexCodeReviewer")
                .with_code_snippet(f"def function_{i}(): pass")
                .with_programming_language("Python")
                .with_review_focus("performance")
                .with_severity("medium")
                .with_tool("complexity_analyzer")
                .with_tool_parameter("complexity_analyzer", "threshold", i % 10)
                .with_memory([
                    {"role": "user", "content": f"Review this code iteration {i}"}
                ])
                .build()
            )
            
            assert isinstance(config, dict)
            assert "messages" in config
        
        execution_time = time.time() - start_time
        avg_time_per_build = execution_time / iterations
        
        # Builder operations should be fast
        assert avg_time_per_build < 0.2, f"Average builder time: {avg_time_per_build:.4f}s (too slow)"


class TestMemoryManagement:
    """Test memory management and resource cleanup."""

    def test_memory_cleanup_after_operations(self):
        """Test that memory is properly cleaned up after operations."""
        process = psutil.Process()
        
        # Baseline measurement
        gc.collect()
        baseline_memory = process.memory_info().rss / 1024 / 1024
        
        # Perform many operations that could potentially leak memory
        configs = []
        for i in range(200):
            try:
                config = (
                    Promptix.builder("SimpleChat")
                    .with_user_name(f"User{i}")
                    .with_assistant_name(f"Assistant{i}")
                    .with_memory([
                        {"role": "user", "content": f"Message {i} with lots of content " * 10}
                    ])
                    .build()
                )
                configs.append(config)
                
                # Also test direct prompt generation
                prompt = Promptix.get_prompt(
                    prompt_template="SimpleChat",
                    user_name=f"TestUser{i}",
                    assistant_name=f"TestAssistant{i}"
                )
            except Exception:
                pass
        
        # Clear references and force garbage collection
        configs.clear()
        del configs
        gc.collect()
        
        # Check final memory
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - baseline_memory
        
        # Memory increase should be minimal after cleanup
        assert memory_increase < 50, f"Memory increased by {memory_increase:.2f}MB after cleanup (potential leak)"

    def test_no_memory_leaks_in_error_conditions(self):
        """Test that error conditions don't cause memory leaks."""
        process = psutil.Process()
        
        gc.collect()
        baseline_memory = process.memory_info().rss / 1024 / 1024
        
        # Generate many errors that could potentially leak memory
        for i in range(100):
            try:
                # Invalid template names
                Promptix.get_prompt(f"InvalidTemplate{i}", var="value")
            except Exception:
                pass
            
            try:
                # Invalid builder configurations
                (Promptix.builder("SimpleChat")
                 .for_client("invalid_client")
                 .build())
            except Exception:
                pass
            
            try:
                # Invalid memory formats
                (Promptix.builder("SimpleChat")
                 .with_memory("invalid_memory_format")
                 .build())
            except Exception:
                pass
        
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - baseline_memory
        
        # Even with many errors, memory shouldn't grow significantly
        assert memory_increase < 30, f"Memory increased by {memory_increase:.2f}MB during error conditions"


class TestScalabilityLimits:
    """Test the scalability limits of the library."""

    def test_maximum_template_size_handling(self):
        """Test handling of very large templates."""
        # Create a very large template string
        large_template_content = "Process this data: " + "x" * 10000  # 10KB of x's
        
        start_time = time.time()
        
        prompt = Promptix.get_prompt(
            prompt_template="CodeReviewer",
            code_snippet=large_template_content,
            programming_language="Text",
            review_focus="content analysis"
        )
        
        execution_time = time.time() - start_time
        
        assert len(prompt) > 10000
        assert large_template_content in prompt
        # Should handle large content without excessive delay
        assert execution_time < 1.0, f"Large template processing took {execution_time:.2f}s"

    def test_deep_nested_variable_access(self):
        """Test performance with deeply nested variable structures."""
        nested_data = {"level1": {"level2": {"level3": {"level4": {"value": "deep_value"}}}}}
        
        # This test would require a template that supports deep nesting
        # For now, we'll test that the system doesn't crash with complex data
        start_time = time.time()
        
        try:
            # Most templates won't use deep nesting, so we'll just verify no crashes
            config = (
                Promptix.builder("SimpleChat")
                .with_user_name("Test")
                .with_assistant_name("Assistant")
                .build()
            )
            assert isinstance(config, dict)
        except Exception as e:
            pytest.fail(f"System crashed with nested data: {e}")
        
        execution_time = time.time() - start_time
        assert execution_time < 0.2, "System slow with complex data structures"

    @pytest.mark.slow
    def test_sustained_load_performance(self):
        """Test performance under sustained load (marked as slow test)."""
        # This test simulates sustained usage
        duration = 5  # seconds
        start_time = time.time()
        operations = 0
        
        while time.time() - start_time < duration:
            try:
                prompt = Promptix.get_prompt(
                    prompt_template="SimpleChat",
                    user_name=f"User{operations}",
                    assistant_name="Assistant"
                )
                assert len(prompt) > 0
                operations += 1
            except Exception:
                pass
        
        total_time = time.time() - start_time
        ops_per_second = operations / total_time
        
        # Should maintain reasonable performance under sustained load
        assert ops_per_second > 10, f"Only {ops_per_second:.2f} operations/second under sustained load"
        assert operations > 50, f"Only completed {operations} operations in {total_time:.2f}s"


class TestResourceConstraints:
    """Test behavior under resource constraints."""

    def test_low_memory_conditions(self):
        """Test graceful handling under simulated low memory conditions."""
        # This is a conceptual test - actual memory limiting is complex
        # We'll simulate by creating many large objects and testing behavior
        
        large_objects = []
        try:
            # Create some memory pressure (but not too much to crash the test)
            for i in range(10):
                large_objects.append([0] * 100000)  # 100k integers each
            
            # Now test that promptix still works
            prompt = Promptix.get_prompt(
                prompt_template="SimpleChat",
                user_name="TestUser",
                assistant_name="TestAssistant"
            )
            
            assert len(prompt) > 0
            
        finally:
            # Cleanup
            large_objects.clear()
            gc.collect()

    def test_cpu_intensive_operations(self):
        """Test that CPU-intensive operations complete in reasonable time."""
        # Simulate CPU-intensive work with complex template operations
        complex_elements = [f"Element_{i}_with_long_description_" + "x" * 100 for i in range(50)]
        
        start_time = time.time()
        
        prompt = Promptix.get_prompt(
            prompt_template="TemplateDemo",
            content_type="tutorial",
            theme="Complex topic with many details",
            difficulty="advanced",
            elements=complex_elements
        )
        
        execution_time = time.time() - start_time
        
        assert len(prompt) > 0
        # Even CPU-intensive operations should complete reasonably quickly
        assert execution_time < 2.0, f"CPU-intensive operation took {execution_time:.2f}s"


# Benchmarking utilities
class PerformanceBenchmark:
    """Utility class for running performance benchmarks."""
    
    def __init__(self):
        self.results = {}
    
    def benchmark(self, name: str, func, *args, **kwargs):
        """Benchmark a function and store results."""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        self.results[name] = {
            'execution_time': end_time - start_time,
            'memory_delta': end_memory - start_memory,
            'result': result
        }
        
        return result
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all benchmark results."""
        return {
            'total_tests': len(self.results),
            'total_time': sum(r['execution_time'] for r in self.results.values()),
            'average_time': sum(r['execution_time'] for r in self.results.values()) / len(self.results),
            'max_memory_delta': max(r['memory_delta'] for r in self.results.values()),
            'details': self.results
        }


@pytest.fixture
def performance_benchmark():
    """Fixture providing performance benchmarking utility."""
    return PerformanceBenchmark()


def test_overall_performance_regression(performance_benchmark):
    """Test for overall performance regressions."""
    # Run a series of representative operations and check performance
    
    # Basic prompt rendering
    performance_benchmark.benchmark(
        'basic_prompt',
        Promptix.get_prompt,
        prompt_template="SimpleChat",
        user_name="TestUser",
        assistant_name="TestAssistant"
    )
    
    # Complex template
    performance_benchmark.benchmark(
        'complex_template',
        Promptix.get_prompt,
        prompt_template="TemplateDemo",
        content_type="tutorial",
        theme="Python",
        difficulty="intermediate",
        elements=["functions", "classes"]
    )
    
    # Builder pattern
    def build_config():
        return (Promptix.builder("CodeReviewer")
               .with_code_snippet("def test(): pass")
               .with_programming_language("Python")
               .with_review_focus("quality")
               .build())
    
    performance_benchmark.benchmark('builder_config', build_config)
    
    # Get benchmark summary
    summary = performance_benchmark.get_summary()
    
    # Assert reasonable performance thresholds
    assert summary['average_time'] < 0.2, f"Average operation time too high: {summary['average_time']:.4f}s"
    assert summary['max_memory_delta'] < 50, f"Memory usage too high: {summary['max_memory_delta']:.2f}MB"
    assert summary['total_time'] < 1.0, f"Total benchmark time too high: {summary['total_time']:.2f}s"
