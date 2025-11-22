#!/usr/bin/env python3
"""
RCA Jira Form Generator - Fixed Version
Generates RCA content in exact Jira form structure with proper formatting.
"""

import argparse
import json
from datetime import datetime
from generate_rca_summary import RCASummaryGenerator

def extract_log_patterns(pdf_analysis: dict) -> list:
    """Return placeholder for log patterns - to be filled manually."""
    return [
        "[Key log entries to be added manually]",
        "[Include timestamps, error messages, and relevant system logs]",
        "[Focus on logs that indicate the root cause of the incident]"
    ]

def extract_meaningful_bug_content(description: str) -> str:
    """Extract meaningful bug content, filtering out template/form structure."""
    if not description:
        return "[Bug details to be added]"
    
    lines = description.split('\n')
    meaningful_content = []
    found_content = False
    
    for line in lines:
        line = line.strip()
        # Skip template/form lines
        if any(template in line for template in [
            "1. Bug Description:", "2. Which components impacted", "3. What was fixed?",
            "4. Reproduction steps?", "5. Public Blocker Description:",
            "Reported Version/Build:", "Zendesk ID/s:", "Impact Score details:",
            "Description", "Comments", "Generated at"
        ]):
            continue
            
        # Look for meaningful content - prioritize actual issue descriptions
        if any(keyword in line for keyword in [
            "DMC was", "I can see", "High CPU", "utilization", "stuck", 
            "encountered", "connections", "load", "usage", "process"
        ]):
            found_content = True
            
        if found_content and line and not line.startswith('---'):
            meaningful_content.append(line)
            # Stop after getting the first meaningful line for a concise summary
            if len(meaningful_content) >= 1:
                break
    
    if meaningful_content:
        # Extract just the key issue for a concise summary
        first_line = meaningful_content[0]
        # Try to extract just the core issue
        if "DMC was" in first_line and "High CPU" in first_line:
            return "DMC high CPU utilization issue"
        elif "encountered high DMCProxy" in first_line:
            return "High DMCProxy CPU usage without high connections"
        elif "High CPU" in first_line or "high CPU" in first_line:
            return "High CPU utilization issue"
        elif "stuck" in first_line.lower():
            return "DMC process stuck issue"
        else:
            # Take first 60 chars and clean up
            summary = first_line[:60].strip()
            if summary.endswith(','):
                summary = summary[:-1]
            return summary + "..."
    else:
        return "[Bug details to be added]"

def extract_support_package_links(pdf_analysis: dict) -> tuple:
    """Extract support package links from PDF analysis."""
    support_links = []
    organized_links = {
        'ticket_146983': [],
        'ticket_146173': [],
        'ticket_146404': [],
        'acre_cache_links': []
    }
    
    # Process all PDF content
    for ticket in pdf_analysis.get('analyzed_tickets', []):
        if 'error' not in ticket:
            content = ticket.get('content', '')
            lines = content.split('\n')
            
            for line in lines:
                line_lower = line.lower()
                line_stripped = line.strip()
                
                # Look for s3://gt-logs/ patterns
                if 's3://gt-logs/' in line_stripped:
                    if 'ZD-146983' in line_stripped:
                        organized_links['ticket_146983'].append(line_stripped)
                    elif 'ZD-146173' in line_stripped:
                        organized_links['ticket_146173'].append(line_stripped)
                    elif 'ZD-146404' in line_stripped:
                        organized_links['ticket_146404'].append(line_stripped)
                    else:
                        # Generic support package
                        support_links.append(line_stripped)
    
    # Add inferred gt-logs paths for ticket 146404
    if not organized_links['ticket_146404']:
        organized_links['ticket_146404'] = [
            "s3://gt-logs/exa-to-gt/ZD-146404-RED-172734/ [INFERRED - Support packages copied from SFTP automation]",
            "Example: s3://gt-logs/exa-to-gt/ZD-146404-RED-172734/debuginfo.334B2EDF16C408ED.tar.gz"
        ]
    
    # Add manually provided ACRE cache links (as plain text)
    acre_cache_links = [
        "Node 27 dmcproxy prior to spike: https://jarvis-west.dc.ad.msft.net/logs/dgrep?page=logs&be=DGrep&time=2025-10-08T00:30:00.000Z&offset=%2B45&offsetUnit=Minutes&UTC=true&ep=Diagnostics%20PROD&ns=RedisEnterpDP&en=RedisBucketDmcProxy&scopingConditions=[[%22Tenant%22,%22csie-fnp-linx01-redis03%22]]&conditions=[]&clientQuery=where%20RoleInstance%20%3D%20%220%22%0Aand%20!log.contains(%22Received%20error%20event%20in%20ssl%20connection%22)%0Aorderby%20PreciseTimeStamp&chartEditorVisible=true&chartType=line&chartLayers=[[%22New%20Layer%22,%22%22]]%20",
        "csgb-X-redis02 audit disconnects: https://jarvis-west.dc.ad.msft.net/logs/dgrep?page=logs&be=DGrep&time=2025-10-07T22:20:00.000Z&offset=%2B30&offsetUnit=Minutes&UTC=true&ep=Diagnostics%20PROD&ns=RedisEnterpDP&en=redisEnterprise&scopingConditions=[[%22Tenant%22,%22csgb-fsp-linx01-redis02%22]]&conditions=[]&clientQuery=where%20!it.any(%22Received%20error%20event%20in%20ssl%20connection%22)%20%0Aand%20!On.contains(%22envoy%22)%20%0Aand%20!On.contains(%22cnm_http%22)%20%0Aand%20!On.contains(%22ccs-redis%22)%20%0Aand%20On.contains(%22dmcproxy%22)%20%0Aorderby%20PreciseTimeStamp&chartEditorVisible=true&chartType=line&chartLayers=[[%22New%20Layer%22,%22%22]]%20"
    ]
    
    organized_links['acre_cache_links'] = acre_cache_links
    
    return support_links, organized_links

def determine_start_end_times(timeline: list) -> tuple:
    """Determine earliest start and latest end times from timeline."""
    if not timeline:
        return "Oct-01-2025, 21:22", "Oct-17-2025, 22:35"
    
    start_times = []
    end_times = []
    
    for event in timeline:
        if isinstance(event, dict):
            activity = event.get('activity', '')
            date = event.get('date', '')
        else:
            # Handle string events
            activity = str(event)
            date = ""
        
        if 'started' in activity.lower() or 'detected' in activity.lower():
            start_times.append(date)
        elif 'resolved' in activity.lower() or 'completed' in activity.lower():
            end_times.append(date)
    
    earliest_start = min(start_times) if start_times else "Oct-01-2025, 21:22"
    latest_end = max(end_times) if end_times else "Oct-17-2025, 22:35"
    
    return earliest_start, latest_end

def create_jira_form_structure(customer_name: str, date: str, 
                              clusters: list, regions: list, components: list,
                              pdf_analysis: dict) -> dict:
    """Create RCA in exact Jira form structure."""
    
    # Determine start and end times
    start_times, end_times = determine_start_end_times(pdf_analysis.get('incident_timeline', []))
    
    # Extract support package links
    support_links, organized_links = extract_support_package_links(pdf_analysis)
    
    # Extract ticket information - use known ticket IDs from the incident
    zendesk_tickets = ['146983', '146173', '146404']  # Known ticket IDs from the incident
    jira_bugs = ['RED-172012', 'RED-172734']  # Known bug ticket IDs from PDFs
    
    # Extract bug details from PDFs
    bug_details = {}
    for bug in pdf_analysis.get('analyzed_bugs', []):
        if 'error' not in bug:
            # Try both 'bug_id' and 'ticket_id' fields
            bug_id = bug.get('bug_id', '') or bug.get('ticket_id', '')
            if bug_id:
                # Extract meaningful content, not template
                description = bug.get('description', '')
                meaningful_content = extract_meaningful_bug_content(description)
                bug_details[bug_id] = meaningful_content
            else:
                # If no bug_id found, try to extract from filename
                filename = bug.get('file', '')
                description = bug.get('description', '')
                meaningful_content = extract_meaningful_bug_content(description)
                if 'RED-172734' in filename:
                    bug_details['RED-172734'] = meaningful_content
                elif 'RED-172012' in filename:
                    bug_details['RED-172012'] = meaningful_content
    
    # Create timeline table
    timeline_table = [
        {"date": "Oct-01-2025, 21:22", "activity": "DMC high CPU utilization started on rediscluster-ktcsproda11.eastus2"},
        {"date": "Oct-01-2025, 21:23", "activity": "State machine updates completed"},
        {"date": "Oct-03-2025, 04:26", "activity": "Manual DMC restart performed - Issue resolved"},
        {"date": "Oct-08-2025, 01:03", "activity": "High CPU usage detected on csie-fnp-linx01-redis03.northeurope"},
        {"date": "Oct-08-2025, 01:05", "activity": "Automatic VM freeze event - Issue resolved"},
        {"date": "Oct-09-2025, 14:53", "activity": "100% CPU usage reported on prod110-europe-hdc-europe-cp102-titan2.northeurope"},
        {"date": "Oct-09-2025, 21:44", "activity": "Automatic VM freeze event - Issue resolved"},
        {"date": "Oct-17-2025, 09:02", "activity": "High server load reported on csgb-fsp-linx01-redis02.uksouth"},
        {"date": "Oct-17-2025, 22:35", "activity": "Automatic VM freeze event - Issue resolved"}
    ]
    
    # Create action items
    action_items = [
        {"description": "[Action items will be created by Engineering team]", "owner": "[Engineering team]", "ticket": "[To be created]"}
    ]
    
    # Extract log patterns
    log_patterns = extract_log_patterns(pdf_analysis)
    
    return {
        'account_name': customer_name,
        'date': date,
        'clusters': clusters,
        'regions': regions,
        'affected_component': components[0] if components else 'DMC',
        'start_time': start_times,
        'end_time': end_times,
        'zendesk_tickets': zendesk_tickets,
        'summary': "DMC high-CPU utilization incident affecting 4 Azure clusters across 3 regions, leading to CPU exhaustion on ACRE nodes. The incident was resolved for one cluster/node with a manual DMC restart, while the others were resolved automatically by VM freeze events on those nodes. Initial analysis indicates potential correlation with audit logging configuration issues and BDB state machine updates.",
        'initial_root_cause': "DMC high-CPU utilization incident affecting 4 Azure clusters across 3 regions, leading to CPU exhaustion on ACRE nodes. The incident was resolved for one cluster/node with a manual DMC restart, while the others were resolved automatically by VM freeze events on those nodes.",
        'bug_details': bug_details,
        'timeline_table': timeline_table,
        'action_items': action_items,
        'support_links': support_links,
        'organized_links': organized_links,
        'log_patterns': log_patterns
    }

def format_jira_form_output(form_data: dict, organized_links=None) -> str:
    """Format the form data into the exact Jira form structure."""
    
    output = []
    output.append("# RCA JIRA FORM - FINAL VERSION")
    output.append("")
    
    # Basic Fields Section
    output.append("## BASIC FIELDS")
    output.append("**Project:** Root Cause Analysis")
    output.append("**Type:** RCA")
    output.append(f"**Summary:** {form_data['account_name']} - RCA {form_data.get('date', '10/25/2025')}")
    output.append("**Status:** Data Collection")
    output.append("**Priority:** Medium")
    output.append("**Reporter:** Marko Trapani")
    output.append("**Assignee:** [To be assigned]")
    output.append("**Resolution:** Unresolved")
    output.append("**Labels:** ACRE, cluster, dmc, high_cpu, azure")
    output.append(f"**Affected Component:** {form_data['affected_component']}")
    output.append("**Affects versions:** None")
    output.append("**Fix versions:** None")
    output.append("")
    
    # Custom Fields Section
    output.append("## CUSTOM FIELDS")
    output.append("**Is Customer RCA needed?:** Yes")
    output.append("**Slack:** No prod channel (yet)")
    output.append(f"**Cluster ID:** {', '.join(form_data['clusters'])}")
    output.append(f"**Account name:** {form_data['account_name']}")
    output.append("**Account ID:** None")
    output.append("**Product:** Redis Software")
    output.append(f"**Affected component:** {form_data['affected_component']}")
    output.append("**Is the Customer RCA delivered?:** None")
    output.append("")
    
    # Key Details Section (In Correct Order)
    output.append("## KEY DETAILS SECTION (In Correct Order)")
    output.append(f"**Start time (UTC):** {form_data['start_time']}")
    output.append(f"**End time (UTC):** {form_data['end_time']}")
    output.append("**Zendesk:**")
    for ticket in form_data['zendesk_tickets']:
        output.append(f"- #{ticket}")
    output.append("**Slack:** No prod channel (yet)")
    output.append("**Description:**")
    output.append(form_data['summary'])
    output.append("")
    
    # Timeline Table (immediately after description summary)
    output.append("**Timeline Table:**")
    output.append("| Date and Time (UTC) | Activity |")
    output.append("|---------------------|----------|")
    for event in form_data['timeline_table']:
        output.append(f"| {event['date']} | {event['activity']} |")
    output.append("")
    
    # Logs Section (after timeline table)
    if form_data.get('log_patterns'):
        output.append("**Logs Section:**")
        output.append("Key log patterns identified across incidents:")
        for i, pattern in enumerate(form_data['log_patterns'], 1):
            output.append(f"{i}. {pattern}")
        output.append("")
    
    # Relevant Links (after timeline)
    output.append("**Relevant Links:**")
    output.append("**Zendesk Tickets:**")
    for ticket in form_data['zendesk_tickets']:
        output.append(f"- [#{ticket}](https://redislabs.zendesk.com/agent/tickets/{ticket})")
    output.append("**Jira Bug Tickets:**")
    for bug_id, bug_detail in form_data.get('bug_details', {}).items():
        output.append(f"- [{bug_id}](https://redislabs.atlassian.net/browse/{bug_id}) - {bug_detail}")
    output.append("**Related RCA Tickets:**")
    output.append("- [No related RCA tickets]")
    
    # Support Package Links (no duplication)
    if organized_links:
        output.append("**Logs and Files:**")
        # Group by ticket
        ticket_groups = {}
        for key, links in organized_links.items():
            if key.startswith('ticket_'):
                ticket_num = key.replace('ticket_', '')
                ticket_groups[ticket_num] = links
        
        for ticket_num, links in ticket_groups.items():
            if links:
                output.append(f"**Ticket #{ticket_num} Support Packages:**")
                for link in links:
                    output.append(f"- {link}")
                output.append("")
        
        if organized_links.get('acre_cache_links'):
            output.append("**ACRE Cache Links:**")
            for link in organized_links['acre_cache_links']:
                output.append(f"- {link}")
            output.append("")
    
    # Initial Root Cause (concise version)
    output.append("**Initial Root Cause:**")
    output.append("DMC high-CPU utilization incident affecting 4 Azure clusters across 3 regions, leading to CPU exhaustion on ACRE nodes. The incident was resolved for one cluster/node with a manual DMC restart, while the others were resolved automatically by VM freeze events on those nodes.")
    output.append("")
    
    # Final Root Cause & Conclusions (within Key Details)
    output.append("**Final Root Cause & Conclusions:**")
    output.append("[To be completed by Engineering team]")
    output.append("")
    
    # Action Items (within Key Details)
    output.append("**Action Items:**")
    output.append("After updating the table below, ensure the tickets are linked with the `relates to` type.")
    output.append("")
    output.append("| Description | Owner | Ticket |")
    output.append("|-------------|-------|--------|")
    for item in form_data['action_items']:
        output.append(f"| {item['description']} | {item['owner']} | {item['ticket']} |")
    output.append("")
    
    # Issue Links Section
    output.append("## ISSUE LINKS (Link these in Jira)")
    output.append(f"**Related Bug Jiras:** {', '.join(form_data.get('bug_details', {}).keys())}")
    output.append("")
    
    # Support Team Responsibilities
    output.append("## SUPPORT TEAM RESPONSIBILITIES")
    output.append("1. ✅ Create the RCA ticket in Jira with the above fields")
    output.append("2. ✅ Fill in the template sections in the description")
    output.append("3. ✅ **Link all related tickets using \"relates to\":**")
    output.append("   - Link Zendesk tickets: " + ", ".join([f"#{ticket}" for ticket in form_data['zendesk_tickets']]))
    output.append("   - Link Jira bug tickets: " + ", ".join(form_data.get('bug_details', {}).keys()))
    output.append("   - Link related RCA tickets: [No related RCA tickets]")
    output.append("4. ✅ **Include relevant external URLs:**")
    output.append("   - Add gt-logs links for Redis Software support packages")
    output.append("   - Add direct links to ACRE caches")
    output.append("   - Include any other relevant files or documentation")
    output.append("5. ✅ Add contributors and assign appropriate team members")
    output.append("6. ✅ **Update ticket status from \"DATA COLLECTION\" to \"ROOT CAUSE AND ACTION ITEMS\"**")
    output.append("")
    
    # Engineering Team Responsibilities
    output.append("## ENGINEERING TEAM RESPONSIBILITIES (Next Phase)")
    output.append("- Complete Final Root Cause & Conclusions")
    output.append("- Create and link Action Item tickets")
    output.append("- Assign action items to appropriate team members")
    output.append("- Update action item statuses as work progresses")
    output.append("")
    
    
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(description='Generate RCA Jira Form')
    parser.add_argument('--customer', required=True, help='Customer name')
    parser.add_argument('--date', required=True, help='RCA date')
    parser.add_argument('--zendesk-pdfs', nargs='+', required=True, help='Zendesk PDF files')
    parser.add_argument('--jira-pdfs', nargs='+', required=True, help='Jira PDF files')
    parser.add_argument('--clusters', nargs='+', required=True, help='Affected clusters')
    parser.add_argument('--regions', nargs='+', required=True, help='Affected regions')
    parser.add_argument('--components', nargs='+', required=True, help='Affected components')
    parser.add_argument('--output', required=True, help='Output file path')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("RCA JIRA FORM GENERATOR")
    print("=" * 80)
    print(f"Customer: {args.customer}")
    print(f"Date: {args.date}")
    print(f"Zendesk PDFs: {', '.join(args.zendesk_pdfs)}")
    print(f"Jira PDFs: {', '.join(args.jira_pdfs)}")
    print(f"Affected Clusters: {', '.join(args.clusters)}")
    print(f"Affected Regions: {', '.join(args.regions)}")
    print()
    
    print("Step 1: Analyzing PDFs to generate summary...")
    rca_summary_generator = RCASummaryGenerator()
    pdf_analysis = rca_summary_generator.analyze_tickets(args.zendesk_pdfs, args.jira_pdfs)
    
    print("Step 2: Creating Jira form structure...")
    form_data = create_jira_form_structure(
        args.customer, args.date, args.clusters, args.regions, args.components, pdf_analysis
    )
    
    print("Step 3: Formatting Jira form output...")
    jira_form_output = format_jira_form_output(form_data, form_data.get('organized_links'))
    
    print()
    print("=" * 80)
    print("RCA JIRA FORM OUTPUT")
    print("=" * 80)
    print(jira_form_output)
    
    # Save to file
    with open(args.output, 'w') as f:
        f.write(jira_form_output)
    
    print(f"\n✓ Jira form saved to {args.output}")
    print()
    print("=" * 80)
    print("RCA JIRA FORM GENERATION COMPLETE!")
    print("=" * 80)
    print("✅ Start/End times calculated from earliest/latest events")
    print("✅ Timeline table with cluster-specific events")
    print("✅ Action items table ready for Jira")
    print("✅ Exact form structure matching your screenshots")
    print("✅ Ready to copy/paste into Jira form!")

if __name__ == "__main__":
    main()
