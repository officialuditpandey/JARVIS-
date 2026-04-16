#!/usr/bin/env python3
"""
Corrected main loop section with proper indentation
"""

# Read current file
with open('jarvis_final.py', 'r') as f:
    lines = f.readlines()

# Find the problematic section and fix it
corrected_lines = []
for i, line in enumerate(lines):
    if i >= 1960 and i <= 1980:
        if i == 1965:
            # Fix the indentation issue
            corrected_lines.append("                # Bypass fuzzy matching, send directly to brain")
        elif i == 1966:
            corrected_lines.append("                ")
        elif i == 1967:
            corrected_lines.append("            try:")
        elif i == 1968:
            corrected_lines.append("        # Handle application launch commands")
        elif i == 1969:
            corrected_lines.append("        if \"open\" in query or \"launch\" in query or \"start\" in query:")
        else:
            corrected_lines.append(line)

# Write the corrected file
with open('jarvis_final.py', 'w') as f:
    for i, line in enumerate(lines):
        if i >= 1960 and i <= 1980:
            if i == 1965:
                f.write("                # Bypass fuzzy matching, send directly to brain")
            elif i == 1966:
                f.write("                ")
            elif i == 1967:
                f.write("            try:")
            elif i == 1968:
                f.write("        # Handle application launch commands")
            elif i == 1969:
                f.write("        if \"open\" in query or \"launch\" in query or \"start\" in query:")
            else:
                f.write(line)
        else:
            f.write(line)

print("Main loop indentation fixed!")
print("To apply this fix:")
print("1. Copy the corrected lines from jarvis_final.py")
print("2. Replace lines 1965-1979 with the corrected version")
print("3. Test volume command again")
