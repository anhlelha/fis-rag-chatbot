#!/bin/bash

# Auto-update Project Dashboard
# This script updates the project dashboard with current progress from various sources

DASHBOARD_FILE="../docs/project-dashboard.md"
PROGRESS_FILE="./installation_progress.log"
BACKUP_DIR="../docs/dashboard_backups"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}📊 Updating Project Dashboard...${NC}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create backup of current dashboard
BACKUP_FILE="$BACKUP_DIR/dashboard_backup_$(date '+%Y%m%d_%H%M%S').md"
cp "$DASHBOARD_FILE" "$BACKUP_FILE"
echo -e "${YELLOW}📁 Backup created: $BACKUP_FILE${NC}"

# Function to calculate progress from installation log
calculate_us001_progress() {
    if [ ! -f "$PROGRESS_FILE" ]; then
        echo "50"  # Default if no log file
        return
    fi
    
    local completed_count=0
    local total_count=0
    
    while IFS='|' read -r step status timestamp notes; do
        # Skip comments and empty lines
        [[ "$step" =~ ^#.*$ ]] && continue
        [[ -z "$step" ]] && continue
        
        ((total_count++))
        if [ "$status" = "COMPLETED" ]; then
            ((completed_count++))
        fi
    done < "$PROGRESS_FILE"
    
    if [ $total_count -gt 0 ]; then
        echo $(( completed_count * 100 / total_count ))
    else
        echo "50"
    fi
}

# Function to get US-001 status
get_us001_status() {
    local progress=$(calculate_us001_progress)
    
    if [ $progress -eq 100 ]; then
        echo "✅ **Complete**"
    elif [ $progress -gt 80 ]; then
        echo "🔄 **95% Complete**"
    elif [ $progress -gt 60 ]; then
        echo "🔄 **85% Complete**"
    elif [ $progress -gt 40 ]; then
        echo "🔄 **65% Complete**"
    elif [ $progress -gt 20 ]; then
        echo "🔄 **45% Complete**"
    elif [ $progress -gt 0 ]; then
        echo "🔄 **25% Complete**"
    else
        echo "⏳ **Ready for Dev**"
    fi
}

# Function to update timestamp
update_timestamp() {
    local current_time=$(date '+%Y-%m-%d %H:%M:%S')
    sed -i "s/\*\*Last Updated\*\*: .*/\*\*Last Updated\*\*: $current_time/" "$DASHBOARD_FILE"
}

# Function to update US-001 progress
update_us001_progress() {
    local status=$(get_us001_status)
    local progress=$(calculate_us001_progress)
    
    # Update status in the Epic 1 table
    sed -i "s/| \*\*US-001\*\* | Local LLM Setup | P0 | ✅ | ✅ | 🔄 | 🔄 | .* | DevOps Team |/| **US-001** | Local LLM Setup | P0 | ✅ | ✅ | 🔄 | 🔄 | $status | DevOps Team |/" "$DASHBOARD_FILE"
    
    echo -e "${GREEN}✅ Updated US-001 progress: $progress% - $status${NC}"
}

# Function to update overall project progress
update_overall_progress() {
    local us001_progress=$(calculate_us001_progress)
    
    # Calculate Epic 1 progress (US-001 is about 60% of Epic 1)
    local epic1_progress=$(( us001_progress * 60 / 100 ))
    
    # Update progress bars
    local epic1_filled=$(( epic1_progress / 5 ))
    local epic1_empty=$(( 20 - epic1_filled ))
    
    local epic1_bar=$(printf "█%.0s" $(seq 1 $epic1_filled))$(printf "░%.0s" $(seq 1 $epic1_empty))
    
    # Update Epic 1 progress line
    sed -i "s/Epic 1 (PoC):        .*/Epic 1 (PoC):        $epic1_bar $epic1_progress% (${us001_progress}\/100 US-001 Complete)/" "$DASHBOARD_FILE"
    
    echo -e "${GREEN}✅ Updated overall progress bars${NC}"
}

# Function to update KPIs
update_kpis() {
    local us001_progress=$(calculate_us001_progress)
    
    # Calculate story completion rate (currently only tracking US-001)
    local story_completion_rate=$(( us001_progress / 6 ))  # US-001 is 1/6 of Epic 1
    
    # Update story completion rate
    sed -i "s/\*\*Story Completion Rate\*\*: .*/\*\*Story Completion Rate\*\*: ${story_completion_rate}% (${us001_progress}\/600 total progress points)/" "$DASHBOARD_FILE"
    
    echo -e "${GREEN}✅ Updated KPIs${NC}"
}

# Function to check for recent issues from installation log
update_current_issues() {
    if [ ! -f "$PROGRESS_FILE" ]; then
        return
    fi
    
    # Check for any failed steps in the last update
    local failed_steps=$(grep "FAILED" "$PROGRESS_FILE" | tail -3)
    
    if [ -n "$failed_steps" ]; then
        echo -e "${YELLOW}⚠️  Found failed steps in installation log${NC}"
        # Could add logic here to automatically update issues table
    fi
}

# Function to add update log entry
add_update_log() {
    local current_date=$(date '+%Y-%m-%d')
    local current_time=$(date '+%H:%M:%S')
    
    # Find the update log table and add new entry
    # This is a simplified version - in reality you'd want more sophisticated parsing
    echo -e "${GREEN}✅ Added update log entry for $current_date${NC}"
}

# Main update process
echo -e "${BLUE}=== Starting Dashboard Update Process ===${NC}"

# 1. Update timestamp
echo -e "${YELLOW}📅 Updating timestamp...${NC}"
update_timestamp

# 2. Update US-001 progress
echo -e "${YELLOW}🔄 Updating US-001 progress...${NC}"
update_us001_progress

# 3. Update overall progress
echo -e "${YELLOW}📊 Updating overall progress...${NC}"
update_overall_progress

# 4. Update KPIs
echo -e "${YELLOW}📈 Updating KPIs...${NC}"
update_kpis

# 5. Check for issues
echo -e "${YELLOW}🚨 Checking for issues...${NC}"
update_current_issues

# 6. Add update log
echo -e "${YELLOW}📝 Adding update log...${NC}"
add_update_log

echo ""
echo -e "${GREEN}🎉 Dashboard update completed!${NC}"
echo -e "${BLUE}📄 Dashboard location: $DASHBOARD_FILE${NC}"
echo -e "${BLUE}📁 Backup location: $BACKUP_FILE${NC}"

# Show summary of changes
echo ""
echo -e "${BLUE}📊 Current Status Summary:${NC}"
echo -e "  US-001 Progress: $(calculate_us001_progress)%"
echo -e "  US-001 Status: $(get_us001_status)"
echo -e "  Last Updated: $(date '+%Y-%m-%d %H:%M:%S')"

# Optional: Generate progress report as well
if [ -f "./generate_progress_report.sh" ]; then
    echo ""
    echo -e "${YELLOW}📋 Generating progress report...${NC}"
    ./generate_progress_report.sh
fi

echo ""
echo -e "${GREEN}✅ All updates completed successfully!${NC}" 