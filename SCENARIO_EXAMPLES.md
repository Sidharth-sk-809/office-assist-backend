# Example Scenarios for Different Industries

This document provides ready-to-use scenario templates that organizations can customize for their specific context.

---

## Technology/SaaS Companies

### Scenario 1: Production Database Outage

**Title:** Critical Production Database Outage - Saturday 2 AM

**Description:** A critical production database became unresponsive, affecting all users trying to access their accounts. You're on-call duty.

**Technical Context:**
- Production environment: PostgreSQL database with 50GB dataset
- Peak load: 5,000 concurrent users
- Last backup: 30 minutes ago
- Monitoring alerts: CPU utilization spiked to 100%, query latency increased 100x
- Customer impact: Users unable to login for 15 minutes before detection

**Company Solution:**

Step 1 (0-2 min): **Immediate Response**
- On-call engineer alerted via PagerDuty
- Initiated war room in Slack #incidents channel
- Notified customer success team about potential outage

Step 2 (2-5 min): **Diagnosis**
- SSH into database server
- Ran `SELECT * FROM pg_stat_statements` to identify slow queries
- Found a recent production query doing full table scan (missing index)
- Query: `SELECT * FROM user_events WHERE timestamp > now() - interval '24 hours'`

Step 3 (5-8 min): **Mitigation**
- Added index: `CREATE INDEX idx_user_events_timestamp ON user_events(timestamp)`
- Connection pool recovered gradually
- Queries returned to normal latency

Step 4 (8-15 min): **Communication**
- Updated status page to "Resolved"
- Sent customer communication via email
- documented initial findings in #incidents

Step 5 (Next day): **Root Cause Analysis**
- Discovered: New feature deployed 4 hours prior that performs 24-hour event lookup
- Action items: Review deployment process, require index verification before production, improve monitoring for missing indexes

**Challenges Faced:**
- Time pressure: Customer impact increasing by second
- Incomplete information: Took 2 minutes to identify root cause
- Communication: Needed to coordinate across on-call, customer success, and engineering
- Decision-making: Considered if rebuild would be faster (would have been wrong - took only 2 min to fix with index)

**Lessons Learned:**
- Missing indexes are common source of production incidents - catch in staging
- Monitor query execution plans in production continuously
- Index rollout should be part of deployment checklists
- On-call procedures and war room communication reduce MTTR significantly
- Regular incident simulations improve team response time

**Difficulty Level:** Hard  
**Category:** Technical  
**Tags:** database, incident-response, performance, postgresql

---

### Scenario 2: Security Vulnerability Discovery

**Title:** Critical Security Vulnerability Found in Production

**Description:** Your security team discovered a potential SQL injection vulnerability in the user search functionality. The vulnerability may have exposed customer data.

**Technical Context:**
- Vulnerability discovered via bug bounty program
- Affected endpoint: `GET /api/search?query=user_name`
- Query constructed: `SELECT * FROM users WHERE name LIKE '%' + input + '%'`
- Database contains PII: names, emails, phone numbers
- Application running since version 2.5.0 (3 months)
- Unknown if vulnerability was exploited

**Company Solution:**

Step 1 (0-1 hour): **Immediate Response**
- Security team files incident P1 and declares security incident
- Timeline: 2.5.0 release was 3 months ago
- Begin forensic analysis: Check WAF logs for suspicious patterns
- Notify CEO, Legal, and Privacy teams

Step 2 (1-2 hours): **Containment**
- Temporarily disable user search endpoint
- Deploy hotfix: Use parameterized queries for all search
- Roll out fixed version 2.5.1
- Monitor application logs for any exploitation attempts

Step 3 (2-6 hours): **Investigation**
- Examine access logs for past 90 days
- Query for patterns indicating SQL injection attempts
- Found: 3 suspicious IPs making unusual search queries 6 weeks ago
- Determine likelihood of data exfiltration

Step 4 (6-12 hours): **Customer Communication**
- Prepare disclosure statement (required by privacy laws)
- Notify affected customers via email
- offer free credit monitoring if data was exfiltrated
- Publish blog post about the fix

Step 5 (Next week): **Prevention**
- Implement parameterized queries company-wide
- Add SQL injection testing to automated security tests
- Require security code review for any SQL queries
- Quarterly security audits going forward

**Challenges Faced:**
- Legal complexity: CCPA, GDPR, HIPAA compliance requirements
- Customer trust: Need to disclose incident but minimize panic
- Rapid response: Need to contain while gathering information
- Technical debt: Similar vulnerabilities likely in other endpoints
- Team coordination: Many departments involved (legal, privacy, engineering, comms)

**Lessons Learned:**
- Parameterized queries/ORMs should be mandatory for all new code
- Regular security audits catch issues before external discovery
- Incident response playbook crucial for crisis management
- Customer communication transparency important for trust
- Security is everyone's responsibility, not just security team
- Budget time for addressing technical debt before it becomes security liability

**Difficulty Level:** Hard  
**Category:** Security  
**Tags:** security, incident-response, compliance, sql-injection

---

### Scenario 3: Handling Overwhelming Feature Requests

**Title:** Customer Successfully Demands New Feature - Now What?

**Description:** Your largest customer (30% of revenue) is demanding a complex new feature by end of month. Your product roadmap is fully committed and the feature requires significant architectural changes.

**Technical Context:**
- Customer value: $500K/year annual revenue
- Timeline: 4 weeks until their critical event
- Feature: Real-time collaboration on documents (requires WebSocket architecture changes)
- Current team capacity: 8 engineers, already committed to Q1 roadmap
- Risk: Customer threatens to switch if feature not delivered

**Company Solution:**

Step 1 (Day 1): **Assess Impact**
- Engineering lead meets with customer to fully understand requirements
- Product lead evaluates roadmap impact: Would delay 3 other features
- Finance calculates: Losing customer = $500K/year loss + risk of references
- Determine: Feature is feasible but requires creative resource allocation

Step 2 (Day 1-2): **Decision & Communication**
- Leadership meeting: Commit to delivering MVP version by deadline
- Communicate to other customers: Some features delayed due to strategic priority
- Set expectations: MVP version, full version in 8 weeks
- Get executive sponsorship and commitment

Step 3 (Week 1): **Technical Design**
- Architecture review: Plan WebSocket implementation
- Identify core functionality: Prioritize which collab features essential for MVP
- Estimate: MVP = 4 weeks of work (80 engineer-hours)
- Decide: Pull 2 engineers from less critical initiatives

Step 4 (Week 2-4): **Implementation**
- Dedicated team of 3 engineers (1 new hiring temp contractor + 2 moved from roadmap)
- Daily standups with customer to manage expectations
- Aggressive testing schedule to catch issues early
- Bi-weekly demos to show progress

Step 5 (Week 4): **Launch & Support**
- MVP launched for customer's event
- Dedicated support during their event weekend
- Gather feedback for full feature expansion
- Post-mortem: Identify how to better predict/plan for such requests

**Challenges Faced:**
- Roadmap disruption: 3 features delayed, upset other customers
- Team morale: New directive affects previously committed work
- Technical risk: WebSocket changes affect system stability
- Resource constraints: Can't hire fast enough for contractor role
- Quality concerns: Aggressive timeline increases bug risk
- Customer management: Managing expectations on timelines

**Lessons Learned:**
- Strategic accounts need dedicated planning and relationship management
- Technical debt and inflexible architecture limits business agility
- Modular architecture would have made this change easier
- Transparent communication about tradeoffs is critical
- Sometimes customer requests reveal product strategy issues
- Retaining key customers requires calculated risks sometimes
- Document decision-making process for future similar decisions
- Consider building "innovation time" into roadmap for emergencies

**Difficulty Level:** Hard  
**Category:** Project Management  
**Tags:** product-management, customer-relations, technical-debt, strategy

---

## Healthcare/Finance Companies

### Scenario 4: Compliance Audit Finding

**Title:** Annual Compliance Audit Reveals Critical Gaps

**Description:** Your annual HIPAA compliance audit discovered that patient data is being accessed in ways not covered by existing access controls and audit logging.

**Company Solution:**

Step 1: **Immediate Assessment**
- Audit finding: No logging of who accessed what patient records
- Risk level: Critical - violates HIPAA regulations, potential $100K+ fines
- Scope: Affects entire patient records system

Step 2: **Emergency Response**
- Establish compliance tiger team
- Notify legal, compliance, and CISO
- Implement temporary logging to all data access
- Notify audit firm of remediation plan

Step 3: **Root Cause Analysis**
- Historical system built before logging requirement
- Architecture didn't anticipate audit needs
- Retrofit logging architecture
- Implement proper access controls

Step 4: **Remediation**
- Redesign access control layer with comprehensive logging
- Deploy new access control system
- Audit all historical access (90 days)
- Verify no suspicious access patterns

Step 5: **Prevention**
- Quarterly compliance check-ins
- Compliance requirements in all architectural reviews
- Automated compliance testing
- Regular audit simulations

---

## Financial Services

### Scenario 5: Handling Account Discrepancy Crisis

**Title:** Millions in Accounts Unreconciled - Customer Panic

**Description:** A data migration issue caused transaction reconciliation to fail for 10,000 accounts. Customers are seeing incorrect balances.

**Technical Context:**
- 10,000 customer accounts affected
- Data migration from legacy system to new system
- Transaction mismatch: ~$2 million in discrepancies
- Customer service flooded with complaints
- Media coverage: Customers tweeting concerns

**Company Response Strategy:**
1. **Immediate Communication:** Acknowledge issue publicly within 1 hour
2. **Diagnosis:** Data pipeline logs show transformation error step 7
3. **Mitigation:** Roll back transactions, reprocess with fix
4. **Customer Service:** Priority support for affected accounts
5. **Root Cause:** Insufficient data migration testing
6. **Prevention:** Mandatory reconciliation testing before future migrations

**Lessons:**
- Pre-flight tests are not optional for financial systems
- Communication speed matters more than perfect information
- Backup and rollback procedures should be tested regularly
- Consider impact on customer trust, not just technical impact

---

## Common Themes Across Scenarios

### Key Learning Points
1. **Incident Response:**
   - Detect quickly
   - Communicate transparently
   - Stabilize immediately
   - Investigate thoroughly
   - Prevent recurrence

2. **Decision-Making Under Pressure:**
   - Gather incomplete information
   - Make calls without perfect data
   - Balance customer needs vs. business constraints
   - Own the decision

3. **Cross-functional Coordination:**
   - Engineering, Product, Support, Legal, Finance
   - Different priorities and constraints
   - Conflict resolution
   - Unified communication

4. **Technical Fundamentals:**
   - Monitoring and observability are critical
   - Testing in production-like environments
   - Rollback capabilities
   - Architecture decisions have long-term consequences

---

## How to Create Scenarios for Your Company

### Template

```
Title: [Specific, memorable crisis/situation]
Description: [What happened, customer impact, urgency level]

Technical Context:
- System/component affected
- Scale (users, data, revenue impact)
- Timeline and detection method
- Initial loss/impact

Company Solution:
1. [Immediate response - minutes]
2. [Diagnosis - why it happened]
3. [Mitigation - fix]
4. [Customer communication - transparency]
5. [Prevention - what changed]

Challenges Faced:
- Time pressure
- Communication complexity
- Resource constraints
- Risk of mistakes
- Team coordination

Lessons Learned:
- Key takeaways
- Process improvements
- Architecture changes
- Team learnings
- Business implications

Difficulty Level: Easy/Medium/Hard
Category: [Technical/HR/Project Management/Security/etc.]
Tags: [relevant keywords]
```

### Tips for Your Scenarios

1. **Use real situations** - Employees can tell when scenarios are made up
2. **Include the uncomfortable parts** - Conflicting priorities, poor options
3. **Show the learning** - How did company improve after this?
4. **Be honest about mistakes** - Builds credibility
5. **Include different domains** - Not all tech scenarios
6. **Range of difficulties** - Easy to build confidence, hard to develop critical thinking
7. **Update scenarios** - Industry changes, new technologies, new risks

---

## Quick Scenario Checklist

When creating a scenario, ensure you have:

- [ ] Real situation from company history (or realistic composite)
- [ ] Clear business/customer impact
- [ ] Technical complexity appropriate for audience
- [ ] Company's actual solution approach
- [ ] Documented challenges and decisions
- [ ] Lessons learned with implementation
- [ ] Appropriate difficulty level
- [ ] Relevant tags for filtering
- [ ] Review by subject matter expert
- [ ] Tested with sample submission

---

## Using These Templates

1. **Copy the template** that matches your situation
2. **Fill in your specific details** (company names, systems, numbers)
3. **Have SME review** for accuracy
4. **Create in system** using `/scenarios/create` endpoint
5. **Pilot with team** before rolling out to new hires
6. **Iterate based on feedback** from employee submissions

---

## More Scenario Ideas to Consider

- Crisis communication in crisis
- Hiring/Team building challenges
- Customer escalation management
- Technical debt decisions
- Architecture migration
- Team conflict resolution
- Resource allocation decisions
- Partnership/vendor issues
- Regulatory changes
- Market pivots
- Competitor threats
- Employee performance issues
