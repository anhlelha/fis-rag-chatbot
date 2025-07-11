#!/bin/bash

# Generate Progress Report from installation log

PROGRESS_FILE="./installation_progress.log"
REPORT_FILE="../docs/deployment/us-001-progress-report.md"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "📊 Generating US-001 Installation Progress Report..."

# Check if progress file exists
if [ ! -f "$PROGRESS_FILE" ]; then
    echo "❌ Progress file not found: $PROGRESS_FILE"
    exit 1
fi

# Create report header
cat > "$REPORT_FILE" << 'EOF'
# 📊 US-001 Installation Progress Report

**Generated**: $(date '+%Y-%m-%d %H:%M:%S')  
**Epic**: 1 - Proof of Concept  
**User Story**: US-001 - Local LLM Setup  
**Target Server**: CentOS 8 (IP: 10.14.190.5)  

---

## 📈 Installation Progress

EOF

# Count completed, failed, and in-progress steps
completed_count=0
failed_count=0
in_progress_count=0
not_started_count=0
total_steps=0

# Process each step
echo "## 🔧 Step-by-Step Status" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

while IFS='|' read -r step status timestamp notes; do
    # Skip comments and empty lines
    [[ "$step" =~ ^#.*$ ]] && continue
    [[ -z "$step" ]] && continue
    
    ((total_steps++))
    
    case "$status" in
        "COMPLETED")
            ((completed_count++))
            status_icon="✅"
            status_color="$GREEN"
            ;;
        "FAILED")
            ((failed_count++))
            status_icon="❌"
            status_color="$RED"
            ;;
        "IN_PROGRESS")
            ((in_progress_count++))
            status_icon="🔄"
            status_color="$YELLOW"
            ;;
        *)
            ((not_started_count++))
            status_icon="⏳"
            status_color="$NC"
            ;;
    esac
    
    # Map step IDs to descriptions
    case "$step" in
        "PRE_INSTALL") description="Pre-Installation Checks" ;;
        "STEP_01") description="User Management" ;;
        "STEP_02") description="Directory Setup" ;;
        "STEP_03") description="Ollama Binary Installation" ;;
        "STEP_04") description="Systemd Service Creation" ;;
        "STEP_05") description="Service Enablement" ;;
        "STEP_06") description="Service Startup" ;;
        "STEP_07") description="Service Health Check" ;;
        "STEP_08") description="Firewall Configuration" ;;
        "STEP_09") description="API Endpoint Testing" ;;
        "STEP_10") description="Model Download" ;;
        "STEP_11") description="Model Response Testing" ;;
        "STEP_12") description="Health Check Script Creation" ;;
        "FINAL_CHECK") description="Final System Verification" ;;
        *) description="$notes" ;;
    esac
    
    # Add to report
    echo "### $status_icon **$step**: $description" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "- **Status**: $status" >> "$REPORT_FILE"
    if [ -n "$timestamp" ]; then
        echo "- **Timestamp**: $timestamp" >> "$REPORT_FILE"
    fi
    if [ -n "$notes" ]; then
        echo "- **Notes**: $notes" >> "$REPORT_FILE"
    fi
    echo "" >> "$REPORT_FILE"
    
    # Console output
    echo -e "${status_color}$status_icon $step: $description - $status${NC}"
    
done < "$PROGRESS_FILE"

# Add summary
cat >> "$REPORT_FILE" << EOF

---

## 📊 Summary Statistics

**Total Steps**: $total_steps  
**Completed**: $completed_count ✅  
**Failed**: $failed_count ❌  
**In Progress**: $in_progress_count 🔄  
**Not Started**: $not_started_count ⏳  

**Success Rate**: $(( completed_count * 100 / total_steps ))%

EOF

# Determine overall status
if [ $failed_count -gt 0 ]; then
    overall_status="❌ FAILED"
    overall_color="$RED"
elif [ $in_progress_count -gt 0 ]; then
    overall_status="🔄 IN PROGRESS"
    overall_color="$YELLOW"
elif [ $completed_count -eq $total_steps ]; then
    overall_status="✅ COMPLETED"
    overall_color="$GREEN"
else
    overall_status="⏳ NOT STARTED"
    overall_color="$NC"
fi

cat >> "$REPORT_FILE" << EOF
**Overall Status**: $overall_status

---

## 🔗 Next Steps

EOF

if [ $completed_count -eq $total_steps ]; then
    cat >> "$REPORT_FILE" << EOF
✅ **Installation Complete!**

1. Update Epic 1 status to "US-001 Complete"
2. Document server configuration details
3. Inform development team of completion
4. Begin planning for US-002: Document Processing Pipeline

### **Ready for US-002 Development**
EOF
elif [ $failed_count -gt 0 ]; then
    cat >> "$REPORT_FILE" << EOF
❌ **Installation Issues Detected**

1. Review failed steps above
2. Check server logs for error details
3. Retry failed steps or troubleshoot
4. Contact system administrator if needed

### **Troubleshooting Required**
EOF
else
    cat >> "$REPORT_FILE" << EOF
🔄 **Installation In Progress**

1. Monitor current installation progress
2. Wait for completion of current steps
3. Review any failures as they occur
4. Prepare for post-installation verification

### **Continue Monitoring**
EOF
fi

cat >> "$REPORT_FILE" << EOF

---

**Report Generated**: \$(date '+%Y-%m-%d %H:%M:%S')  
**Generated By**: Installation Progress Tracker  
**Next Report**: Run \`./generate_progress_report.sh\` again
EOF

echo ""
echo -e "${BLUE}📊 Progress Report Summary:${NC}"
echo -e "  Total Steps: $total_steps"
echo -e "  ${GREEN}Completed: $completed_count${NC}"
echo -e "  ${RED}Failed: $failed_count${NC}"
echo -e "  ${YELLOW}In Progress: $in_progress_count${NC}"
echo -e "  Overall Status: ${overall_color}$overall_status${NC}"
echo ""
echo -e "${BLUE}📄 Report saved to: $REPORT_FILE${NC}" 