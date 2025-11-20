"""
UX Tour Fix Automation System
Reads tour reports and automatically applies fixes based on analysis

This system:
1. Reads tour reports (issues_categorized.json, fix_recommendations.json)
2. Applies auto-fixable issues (layout, performance)
3. Generates manual fix TODO for complex issues
4. Updates tour flow for next run based on what was fixed

Author: Automated UX Testing System
Date: 2025-11-18
"""
import json
import os
import re
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime


class UXTourFixAutomation:
    """Automatically applies fixes based on UX tour analysis"""
    
    def __init__(self, tour_dir: str):
        """
        Args:
            tour_dir: Path to tour results directory (e.g., docs/ux_tours/tour_regular_20251118-120000)
        """
        self.tour_dir = Path(tour_dir)
        self.reports_dir = self.tour_dir / "reports"
        self.analysis_dir = self.tour_dir / "analysis"
        
        if not self.tour_dir.exists():
            raise ValueError(f"Tour directory not found: {tour_dir}")
        
        self.fixes_applied = []
        self.fixes_failed = []
        self.manual_todos = []
        
        print(f"🔧 UX Tour Fix Automation initialized")
        print(f"📁 Tour directory: {self.tour_dir}")
    
    def load_reports(self) -> Dict:
        """Load all tour reports"""
        print("\n📖 Loading tour reports...")
        
        issues_file = self.reports_dir / "issues_categorized.json"
        recommendations_file = self.analysis_dir / "fix_recommendations.json"
        
        if not issues_file.exists():
            raise ValueError(f"Issues report not found: {issues_file}")
        
        with open(issues_file, 'r', encoding='utf-8') as f:
            issues = json.load(f)
        
        recommendations = {}
        if recommendations_file.exists():
            with open(recommendations_file, 'r', encoding='utf-8') as f:
                recommendations = json.load(f)
        
        print(f"✓ Loaded {issues['total_issues']} issues")
        print(f"  - Layout: {len(issues.get('layout_issues', []))}")
        print(f"  - Functional: {len(issues.get('functional_issues', []))}")
        print(f"  - Errors: {len(issues.get('error_issues', []))}")
        print(f"  - Performance: {len(issues.get('performance_issues', []))}")
        
        return {
            'issues': issues,
            'recommendations': recommendations
        }
    
    def apply_all_fixes(self):
        """Apply all auto-fixable issues"""
        print("\n" + "=" * 80)
        print("🔧 APPLYING AUTOMATIC FIXES")
        print("=" * 80)
        
        reports = self.load_reports()
        
        # Apply layout fixes
        self.apply_layout_fixes(reports['issues']['layout_issues'])
        
        # Apply performance fixes
        self.apply_performance_fixes(reports['issues']['performance_issues'])
        
        # Generate manual TODO for functional/error issues
        self.generate_manual_todos(
            reports['issues']['functional_issues'],
            reports['issues']['error_issues']
        )
        
        # Generate summary
        self.generate_fix_summary()
    
    def apply_layout_fixes(self, layout_issues: List[Dict]):
        """Apply automatic layout fixes"""
        print("\n--- Applying Layout Fixes ---")
        
        # Group issues by type
        text_overflow_files = set()
        
        for issue in layout_issues:
            desc = issue['description']
            
            # Extract screen name from description (format: "screen_name: issue")
            if ':' in desc:
                screen_name = desc.split(':')[0].strip()
                issue_text = desc.split(':', 1)[1].strip()
                
                if "text_size" in issue_text.lower() or "text overflow" in issue_text.lower():
                    # Map screen name to KV file
                    kv_file = self.get_kv_file_for_screen(screen_name)
                    if kv_file:
                        text_overflow_files.add(kv_file)
        
        # Apply text overflow fixes
        for kv_file in text_overflow_files:
            success = self.fix_text_overflow_in_file(kv_file)
            if success:
                self.fixes_applied.append({
                    'type': 'layout',
                    'file': kv_file,
                    'fix': 'Added text_size properties to MDLabel widgets'
                })
            else:
                self.fixes_failed.append({
                    'type': 'layout',
                    'file': kv_file,
                    'reason': 'Could not apply fix'
                })
        
        print(f"✓ Applied {len(self.fixes_applied)} layout fixes")
    
    def fix_text_overflow_in_file(self, kv_filename: str) -> bool:
        """
        Fix text overflow issues in KV file by adding text_size properties
        
        Args:
            kv_filename: Name of KV file (e.g., "wallet_screen.kv")
        
        Returns:
            True if file was modified, False otherwise
        """
        kv_path = Path("src/core/kv") / kv_filename
        
        if not kv_path.exists():
            print(f"⚠️  KV file not found: {kv_path}")
            return False
        
        print(f"🔧 Fixing text overflow in {kv_filename}...")
        
        try:
            with open(kv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            modified = False
            new_lines = []
            i = 0
            
            while i < len(lines):
                line = lines[i]
                new_lines.append(line)
                
                # Check if this is an MDLabel declaration
                if 'MDLabel:' in line:
                    # Get indentation
                    indent = len(line) - len(line.lstrip())
                    property_indent = ' ' * (indent + 4)
                    
                    # Check if text_size already exists in this block
                    has_text_size = False
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j]
                        next_indent = len(next_line) - len(next_line.lstrip())
                        
                        # If indent decreases or same as MDLabel, block ended
                        if next_indent <= indent and next_line.strip():
                            break
                        
                        if 'text_size:' in next_line:
                            has_text_size = True
                            break
                        
                        j += 1
                    
                    # If no text_size, add it
                    if not has_text_size:
                        new_lines.append(f"{property_indent}text_size: self.width, None\n")
                        new_lines.append(f"{property_indent}size_hint_y: None\n")
                        new_lines.append(f"{property_indent}height: self.texture_size[1]\n")
                        modified = True
                        print(f"  ✓ Added text_size to MDLabel at line {i+1}")
                
                i += 1
            
            if modified:
                # Write back
                with open(kv_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                print(f"✅ Fixed text overflow in {kv_filename}")
                return True
            else:
                print(f"  No changes needed in {kv_filename}")
                return False
                
        except Exception as e:
            print(f"❌ Error fixing {kv_filename}: {e}")
            return False
    
    def apply_performance_fixes(self, performance_issues: List[Dict]):
        """Apply automatic performance fixes"""
        print("\n--- Applying Performance Fixes ---")
        
        # Identify button debouncing needs
        buttons_needing_debounce = set()
        
        for issue in performance_issues:
            desc = issue['description']
            if "button" in desc.lower():
                # Extract button name if possible
                # This is implementation-specific
                buttons_needing_debounce.add(desc)
        
        # For now, add to manual TODO
        # Full debouncing requires code analysis
        for button_desc in buttons_needing_debounce:
            self.manual_todos.append({
                'type': 'performance',
                'priority': 'high',
                'description': f"Add debouncing to: {button_desc}",
                'suggestion': 'Use @debounce decorator from src.utils.performance.debouncer'
            })
        
        print(f"⚠️  Performance fixes require manual intervention")
        print(f"   Added {len(buttons_needing_debounce)} items to manual TODO")
    
    def generate_manual_todos(self, functional_issues: List[Dict], error_issues: List[Dict]):
        """Generate manual TODO list for complex issues"""
        print("\n--- Generating Manual TODO List ---")
        
        for issue in functional_issues:
            self.manual_todos.append({
                'type': 'functional',
                'priority': 'high',
                'description': issue['description'],
                'screen': issue['screen'],
                'screenshot': issue.get('screenshot', '')
            })
        
        for issue in error_issues:
            self.manual_todos.append({
                'type': 'error',
                'priority': 'critical',
                'description': issue['description'],
                'action': issue['action'],
                'error': issue['error']
            })
        
        print(f"✓ Generated {len(self.manual_todos)} manual TODO items")
    
    def generate_fix_summary(self):
        """Generate comprehensive fix summary"""
        print("\n" + "=" * 80)
        print("📊 FIX APPLICATION SUMMARY")
        print("=" * 80)
        
        summary = f"""
# UX Tour Fix Summary
**Tour Directory**: {self.tour_dir}
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Automatic Fixes Applied: {len(self.fixes_applied)}

"""
        
        if self.fixes_applied:
            summary += "### Successfully Applied\n"
            for fix in self.fixes_applied:
                summary += f"- **{fix['type'].upper()}**: {fix['file']}\n"
                summary += f"  - {fix['fix']}\n\n"
        
        if self.fixes_failed:
            summary += f"\n### Failed Fixes: {len(self.fixes_failed)}\n"
            for fix in self.fixes_failed:
                summary += f"- **{fix['type'].upper()}**: {fix['file']}\n"
                summary += f"  - Reason: {fix['reason']}\n\n"
        
        if self.manual_todos:
            summary += f"\n## Manual TODO: {len(self.manual_todos)} items\n\n"
            
            # Group by type
            by_type = {}
            for todo in self.manual_todos:
                t = todo['type']
                if t not in by_type:
                    by_type[t] = []
                by_type[t].append(todo)
            
            for todo_type, todos in by_type.items():
                summary += f"### {todo_type.upper()} ({len(todos)} items)\n\n"
                for i, todo in enumerate(todos, 1):
                    summary += f"{i}. **[{todo['priority'].upper()}]** {todo['description']}\n"
                    if 'suggestion' in todo:
                        summary += f"   - Suggestion: {todo['suggestion']}\n"
                    if 'screenshot' in todo and todo['screenshot']:
                        summary += f"   - Screenshot: {todo['screenshot']}\n"
                    summary += "\n"
        
        summary += f"""
## Next Steps

1. **Verify Automatic Fixes**
   - Run test suite to ensure fixes don't break functionality
   - Review modified KV files for correctness

2. **Address Manual TODOs**
   - Prioritize CRITICAL and HIGH priority items
   - Use screenshots for visual reference

3. **Run Tour Again**
   - Execute `python scripts/complete_ux_tour.py --user-type regular`
   - Compare results with this tour
   - Verify fixes resolved issues

4. **Iterate**
   - Apply next batch of fixes
   - Continue until all issues resolved

## Files Modified

"""
        
        modified_files = set(fix['file'] for fix in self.fixes_applied)
        for f in sorted(modified_files):
            summary += f"- src/core/kv/{f}\n"
        
        # Save summary
        summary_file = self.tour_dir / "FIX_SUMMARY.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"\n✅ Fix summary saved: {summary_file}")
        print(f"\n📊 Results:")
        print(f"   ✅ Applied: {len(self.fixes_applied)}")
        print(f"   ❌ Failed: {len(self.fixes_failed)}")
        print(f"   📝 Manual TODO: {len(self.manual_todos)}")
    
    def get_kv_file_for_screen(self, screen_name: str) -> str:
        """Map screen name to KV file name"""
        # Convert screen name to KV file format
        # e.g., "wallet" -> "wallet_screen.kv"
        # "create_import_wallet" -> "create_import_wallet_screen.kv"
        
        if not screen_name:
            return ""
        
        # Check if already has _screen
        if screen_name.endswith('_screen'):
            kv_file = f"{screen_name}.kv"
        else:
            kv_file = f"{screen_name}_screen.kv"
        
        # Verify file exists
        kv_path = Path("src/core/kv") / kv_file
        if kv_path.exists():
            return kv_file
        
        # Try without _screen suffix
        kv_file_alt = f"{screen_name}.kv"
        kv_path_alt = Path("src/core/kv") / kv_file_alt
        if kv_path_alt.exists():
            return kv_file_alt
        
        print(f"⚠️  Could not find KV file for screen: {screen_name}")
        return ""


def main():
    """Run fix automation on most recent tour"""
    import argparse
    
    parser = argparse.ArgumentParser(description='UX Tour Fix Automation')
    parser.add_argument('--tour-dir', help='Tour directory path', required=False)
    
    args = parser.parse_args()
    
    if args.tour_dir:
        tour_dir = args.tour_dir
    else:
        # Find most recent tour
        tours_base = Path("docs/ux_tours")
        if not tours_base.exists():
            print("❌ No tours found in docs/ux_tours")
            return
        
        tours = sorted([d for d in tours_base.iterdir() if d.is_dir()], 
                      key=lambda x: x.name, reverse=True)
        
        if not tours:
            print("❌ No tour directories found")
            return
        
        tour_dir = str(tours[0])
        print(f"📂 Using most recent tour: {tour_dir}")
    
    print("=" * 80)
    print("🔧 UX Tour Fix Automation - Starting...")
    print("=" * 80)
    
    automation = UXTourFixAutomation(tour_dir)
    automation.apply_all_fixes()
    
    print("\n" + "=" * 80)
    print("✅ Fix automation complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
