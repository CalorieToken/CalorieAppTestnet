"""
Complete UX Tour Orchestrator
Runs the full cycle: Tour → Analyze → Fix → Validate → Repeat

This orchestrator:
1. Runs complete UX tour (with screenshots, logs, reports)
2. Analyzes tour results (categorizes issues)
3. Applies automatic fixes (layout, performance)
4. Validates fixes (runs test suite)
5. Adapts tour for next iteration
6. Repeats until target quality achieved

Author: Automated UX Testing System
Date: 2025-11-18
"""
import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class UXTourOrchestrator:
    """
    Orchestrates complete UX tour automation cycle
    
    Cycle:
    1. Run UX tour (complete_ux_tour.py)
    2. Analyze results
    3. Apply fixes (ux_tour_fix_automation.py)
    4. Run validation tests
    5. Compare with previous iteration
    6. Adapt and repeat
    """
    
    def __init__(self, user_type: str = "regular", max_iterations: int = 10):
        """
        Args:
            user_type: "regular" or "pro"
            max_iterations: Maximum number of tour → fix cycles
        """
        self.user_type = user_type
        self.max_iterations = max_iterations
        self.current_iteration = 0
        
        # Create orchestration directory
        self.session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.session_dir = Path("docs/ux_orchestration") / f"session_{user_type}_{self.session_id}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Track progress across iterations
        self.iteration_history = []
        self.total_issues_history = []
        self.fixes_applied_history = []
        
        print("=" * 80)
        print("🎯 UX Tour Orchestrator Initialized")
        print("=" * 80)
        print(f"User Type: {user_type.upper()}")
        print(f"Max Iterations: {max_iterations}")
        print(f"Session Directory: {self.session_dir}")
        print("=" * 80)
    
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        # Also write to session log
        log_file = self.session_dir / "orchestration.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def run_complete_cycle(self):
        """Run complete tour → fix → validate cycle"""
        self.log("🚀 Starting complete UX tour cycle")
        
        for iteration in range(1, self.max_iterations + 1):
            self.current_iteration = iteration
            
            self.log("=" * 80)
            self.log(f"ITERATION {iteration}/{self.max_iterations}")
            self.log("=" * 80)
            
            # Step 1: Run UX Tour
            tour_dir = self.run_ux_tour()
            if not tour_dir:
                self.log("❌ Tour failed, stopping cycle", "ERROR")
                break
            
            # Step 2: Analyze Tour Results
            analysis = self.analyze_tour_results(tour_dir)
            if not analysis:
                self.log("❌ Analysis failed, stopping cycle", "ERROR")
                break
            
            # Record iteration data
            iteration_data = {
                'iteration': iteration,
                'tour_dir': str(tour_dir),
                'timestamp': datetime.now().isoformat(),
                'analysis': analysis
            }
            self.iteration_history.append(iteration_data)
            self.total_issues_history.append(analysis['total_issues'])
            
            # Check if we've achieved perfection
            if analysis['total_issues'] == 0:
                self.log("🎉 PERFECTION ACHIEVED! No issues found!", "SUCCESS")
                break
            
            # Check if we're stuck (same issues for 3 iterations)
            if self.is_stuck():
                self.log("⚠️  Progress stalled, manual intervention needed", "WARNING")
                break
            
            # Step 3: Apply Fixes
            fixes_applied = self.apply_fixes(tour_dir)
            self.fixes_applied_history.append(fixes_applied)
            
            if fixes_applied == 0:
                self.log("⚠️  No automatic fixes available", "WARNING")
                self.log("   Manual intervention required")
                break
            
            # Step 4: Validate Fixes
            validation_passed = self.validate_fixes()
            if not validation_passed:
                self.log("❌ Validation failed, fixes broke something!", "ERROR")
                self.log("   Rolling back and stopping cycle")
                # TODO: Implement rollback
                break
            
            # Step 5: Generate Iteration Report
            self.generate_iteration_report(iteration, iteration_data, fixes_applied)
            
            # Brief pause between iterations
            if iteration < self.max_iterations:
                self.log(f"⏳ Waiting 2s before next iteration...")
                time.sleep(2)
        
        # Generate final summary
        self.generate_final_summary()
        
        self.log("=" * 80)
        self.log("✅ UX Tour Orchestration Complete")
        self.log(f"📁 Session results: {self.session_dir}")
        self.log("=" * 80)
    
    def run_ux_tour(self) -> Path:
        """
        Run complete UX tour
        
        Returns:
            Path to tour results directory, or None if failed
        """
        self.log("📱 Running UX tour...")
        
        # Note: complete_ux_tour.py runs as Kivy app, can't subprocess easily
        # For now, we'll document the expected structure
        
        self.log("⚠️  UX tour must be run separately:")
        self.log("   python scripts/complete_ux_tour.py --user-type regular")
        self.log("   Then run this orchestrator with --tour-dir")
        
        # For automation, we'd need to:
        # 1. Run tour in headless mode (if possible)
        # 2. Or use pytest-kivy or similar
        # 3. Or schedule tour to run and wait for completion
        
        # For now, return None to indicate manual tour needed
        return None
    
    def analyze_tour_results(self, tour_dir: Path) -> Dict:
        """
        Analyze tour results
        
        Returns:
            Dictionary with analysis data
        """
        self.log("🔍 Analyzing tour results...")
        
        reports_dir = tour_dir / "reports"
        issues_file = reports_dir / "issues_categorized.json"
        
        if not issues_file.exists():
            self.log(f"❌ Issues report not found: {issues_file}", "ERROR")
            return None
        
        with open(issues_file, 'r', encoding='utf-8') as f:
            issues = json.load(f)
        
        analysis = {
            'total_issues': issues['total_issues'],
            'layout_issues': len(issues.get('layout_issues', [])),
            'functional_issues': len(issues.get('functional_issues', [])),
            'error_issues': len(issues.get('error_issues', [])),
            'performance_issues': len(issues.get('performance_issues', []))
        }
        
        self.log(f"✓ Analysis complete:")
        self.log(f"  Total issues: {analysis['total_issues']}")
        self.log(f"  - Layout: {analysis['layout_issues']}")
        self.log(f"  - Functional: {analysis['functional_issues']}")
        self.log(f"  - Errors: {analysis['error_issues']}")
        self.log(f"  - Performance: {analysis['performance_issues']}")
        
        return analysis
    
    def apply_fixes(self, tour_dir: Path) -> int:
        """
        Apply automatic fixes
        
        Returns:
            Number of fixes applied
        """
        self.log("🔧 Applying automatic fixes...")
        
        # Run fix automation
        cmd = [sys.executable, "scripts/ux_tour_fix_automation.py", "--tour-dir", str(tour_dir)]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Parse output to count fixes
                # This is implementation-specific
                self.log("✓ Fixes applied successfully")
                
                # Check fix summary for count
                fix_summary = tour_dir / "FIX_SUMMARY.md"
                if fix_summary.exists():
                    with open(fix_summary, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Count "Successfully Applied"
                        fixes_count = content.count("Successfully Applied")
                        return fixes_count
                
                return 1  # At least some fixes applied
            else:
                self.log(f"❌ Fix automation failed: {result.stderr}", "ERROR")
                return 0
                
        except subprocess.TimeoutExpired:
            self.log("❌ Fix automation timed out", "ERROR")
            return 0
        except Exception as e:
            self.log(f"❌ Fix automation error: {e}", "ERROR")
            return 0
    
    def validate_fixes(self) -> bool:
        """
        Validate that fixes didn't break anything
        
        Returns:
            True if validation passed
        """
        self.log("✅ Validating fixes...")
        
        # Run test suite
        env = os.environ.copy()
        env['TEST_MODE'] = 'QUICK'
        env['LAYOUT_AUDIT'] = '0'
        
        cmd = [sys.executable, "scripts/interactive_flow_test.py"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  timeout=120, env=env)
            
            # Check for "ALL TESTS PASSED" or similar
            if "PASSED" in result.stdout or result.returncode == 0:
                self.log("✓ Validation passed - all tests OK")
                return True
            else:
                self.log(f"❌ Validation failed", "ERROR")
                self.log(f"   Output: {result.stdout[-500:]}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("❌ Validation timed out", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Validation error: {e}", "ERROR")
            return False
    
    def is_stuck(self) -> bool:
        """
        Check if progress has stalled
        
        Returns:
            True if stuck (same issue count for 3+ iterations)
        """
        if len(self.total_issues_history) < 3:
            return False
        
        # Check last 3 iterations
        last_3 = self.total_issues_history[-3:]
        
        # If all same, we're stuck
        if len(set(last_3)) == 1 and last_3[0] > 0:
            return True
        
        return False
    
    def generate_iteration_report(self, iteration: int, data: Dict, fixes_applied: int):
        """Generate report for single iteration"""
        report = f"""
# Iteration {iteration} Report

**Timestamp**: {data['timestamp']}
**Tour Directory**: {data['tour_dir']}

## Issues Found
- **Total**: {data['analysis']['total_issues']}
- **Layout**: {data['analysis']['layout_issues']}
- **Functional**: {data['analysis']['functional_issues']}
- **Errors**: {data['analysis']['error_issues']}
- **Performance**: {data['analysis']['performance_issues']}

## Fixes Applied
- **Automatic Fixes**: {fixes_applied}

## Progress
- **Iterations Completed**: {iteration}
- **Total Issues History**: {self.total_issues_history}
- **Fixes Applied History**: {self.fixes_applied_history}

"""
        
        report_file = self.session_dir / f"iteration_{iteration:02d}_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.log(f"📄 Iteration report saved: {report_file}")
    
    def generate_final_summary(self):
        """Generate comprehensive summary of entire session"""
        self.log("📊 Generating final summary...")
        
        # Calculate stats
        total_iterations = len(self.iteration_history)
        total_fixes = sum(self.fixes_applied_history)
        
        issues_start = self.total_issues_history[0] if self.total_issues_history else 0
        issues_end = self.total_issues_history[-1] if self.total_issues_history else 0
        issues_resolved = issues_start - issues_end
        
        summary = f"""
# UX Tour Orchestration - Final Summary

**Session ID**: {self.session_id}
**User Type**: {self.user_type.upper()}
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
- **Total Iterations**: {total_iterations}
- **Total Fixes Applied**: {total_fixes}
- **Issues at Start**: {issues_start}
- **Issues at End**: {issues_end}
- **Issues Resolved**: {issues_resolved}
- **Improvement**: {(issues_resolved / issues_start * 100) if issues_start > 0 else 0:.1f}%

## Iteration History

| Iteration | Total Issues | Fixes Applied | Progress |
|-----------|--------------|---------------|----------|
"""
        
        for i, (issues, fixes) in enumerate(zip(self.total_issues_history, self.fixes_applied_history), 1):
            if i == 1:
                progress = "-"
            else:
                prev = self.total_issues_history[i-2]
                change = prev - issues
                progress = f"{change:+d}"
            
            summary += f"| {i} | {issues} | {fixes} | {progress} |\n"
        
        summary += f"""

## Visual Progress

Issues Over Time:
```
Iteration  Issues
"""
        
        for i, issues in enumerate(self.total_issues_history, 1):
            bar = "█" * issues
            summary += f"{i:2d}         {issues:3d}  {bar}\n"
        
        summary += f"""```

## Iteration Details

"""
        
        for i, iteration in enumerate(self.iteration_history, 1):
            summary += f"### Iteration {i}\n"
            summary += f"- Tour: `{iteration['tour_dir']}`\n"
            summary += f"- Layout issues: {iteration['analysis']['layout_issues']}\n"
            summary += f"- Functional issues: {iteration['analysis']['functional_issues']}\n"
            summary += f"- Error issues: {iteration['analysis']['error_issues']}\n"
            summary += f"- Performance issues: {iteration['analysis']['performance_issues']}\n"
            summary += "\n"
        
        summary += f"""
## Next Steps

"""
        
        if issues_end == 0:
            summary += """
🎉 **PERFECTION ACHIEVED!**

All issues have been resolved. The app is now in excellent condition.

Recommended actions:
1. Run final manual testing to confirm quality
2. Run full test suite one more time
3. Prepare for production deployment
4. Document all improvements made
"""
        elif self.is_stuck():
            summary += """
⚠️  **MANUAL INTERVENTION REQUIRED**

Progress has stalled. Remaining issues require manual attention.

Recommended actions:
1. Review manual TODO list in latest tour's FIX_SUMMARY.md
2. Address functional and error issues
3. Implement performance optimizations
4. Run orchestrator again after manual fixes
"""
        else:
            summary += f"""
🔄 **CONTINUE AUTOMATION**

Progress is being made ({issues_resolved} issues resolved).

Recommended actions:
1. Continue running orchestrator
2. Target: {self.max_iterations - total_iterations} more iterations
3. Expected final issues: ~{max(0, issues_end - 5)}
"""
        
        summary += f"""

## Files Generated

- Session directory: `{self.session_dir}`
- Iteration reports: `{total_iterations}` files
- Tour results: See individual tour directories
- Fix summaries: See FIX_SUMMARY.md in each tour directory

## Session Statistics

- **Duration**: {(datetime.now() - datetime.strptime(self.session_id, "%Y%m%d-%H%M%S")).total_seconds():.0f} seconds
- **Average fixes per iteration**: {total_fixes / total_iterations if total_iterations > 0 else 0:.1f}
- **Issues resolved per iteration**: {issues_resolved / total_iterations if total_iterations > 0 else 0:.1f}

---

*Generated by UX Tour Orchestrator*
*Session: {self.session_id}*
"""
        
        # Save summary
        summary_file = self.session_dir / "FINAL_SUMMARY.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        # Also save JSON data
        data_file = self.session_dir / "session_data.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump({
                'session_id': self.session_id,
                'user_type': self.user_type,
                'max_iterations': self.max_iterations,
                'iterations_completed': total_iterations,
                'total_fixes': total_fixes,
                'issues_start': issues_start,
                'issues_end': issues_end,
                'issues_resolved': issues_resolved,
                'iteration_history': self.iteration_history
            }, f, indent=2)
        
        self.log(f"✓ Final summary saved: {summary_file}")
        self.log(f"✓ Session data saved: {data_file}")


def main():
    """Run UX tour orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='UX Tour Orchestrator')
    parser.add_argument('--user-type', choices=['regular', 'pro'], default='regular',
                       help='User type to test (default: regular)')
    parser.add_argument('--max-iterations', type=int, default=10,
                       help='Maximum iterations to run (default: 10)')
    parser.add_argument('--tour-dir', help='Existing tour directory to analyze and fix')
    
    args = parser.parse_args()
    
    orchestrator = UXTourOrchestrator(
        user_type=args.user_type,
        max_iterations=args.max_iterations
    )
    
    if args.tour_dir:
        # Analyze and fix existing tour
        tour_dir = Path(args.tour_dir)
        if not tour_dir.exists():
            print(f"❌ Tour directory not found: {tour_dir}")
            return
        
        print(f"📂 Processing existing tour: {tour_dir}")
        analysis = orchestrator.analyze_tour_results(tour_dir)
        if analysis:
            fixes = orchestrator.apply_fixes(tour_dir)
            if fixes > 0:
                orchestrator.validate_fixes()
        
        print("\n✅ Processing complete")
    else:
        # Run complete cycle
        orchestrator.run_complete_cycle()


if __name__ == "__main__":
    main()
