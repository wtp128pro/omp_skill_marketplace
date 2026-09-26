# LEGAL DISCLAIMERS, LIMITATION OF LIABILITY & TERMS OF USE

**IMPORTANT: PLEASE READ THIS DOCUMENT CAREFULLY BEFORE USING, DOWNLOADING, INSTALLING, EXECUTING, OR CONTRIBUTING TO THIS REPOSITORY OR ANY OF ITS SKILLS, SCRIPTS, PROMPTS, PERSONAS, TEMPLATES, OR UTILITIES.**

By accessing, downloading, installing, copying, or executing any code, skill, persona, prompt, template, or automated workflow contained in this repository (collectively, the "Software"), you explicitly acknowledge, agree to, and accept the terms, conditions, disclaimers, and limitations of liability set forth herein. If you do not agree to these terms, you must immediately cease all access and permanently delete all copies of the Software in your possession.

---

## 1. "AS IS" AND EXPRESS/IMPLIED WARRANTY DISCLAIMER

THE SOFTWARE IS PROVIDED ON AN **"AS IS"** AND **"AS AVAILABLE"** BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, EITHER EXPRESS, IMPLIED, STATUTORY, OR OTHERWISE. 

TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, THE REPOSITORY OWNER(S), AUTHORS, CONTRIBUTORS, AND AFFILIATES (COLLECTIVELY, THE "AUTHORS") EXPRESSLY DISCLAIM ALL WARRANTIES AND CONDITIONS, INCLUDING BUT NOT LIMITED TO:
- ANY IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE, QUIET ENJOYMENT, AND NON-INFRINGEMENT;
- ANY WARRANTIES ARISING OUT OF COURSE OF DEALING, TRADE USAGE, OR PERFORMANCE;
- ANY WARRANTIES THAT THE SOFTWARE WILL MEET YOUR REQUIREMENTS, ACHIEVE ANY INTENDED RESULTS, BE COMPATIBLE OR WORK WITH ANY OTHER SOFTWARE, APPLICATIONS, SYSTEMS, OR DATA;
- ANY WARRANTIES THAT THE OPERATION OR EXECUTION OF THE SOFTWARE WILL BE UNINTERRUPTED, TIMELY, SECURE, ACCURATE, FREE OF HARMFUL CODE, BUGS, ERRORS, OR DEFECTS, OR THAT DEFECTS WILL BE DETECTED OR CORRECTED.

NO ORAL OR WRITTEN INFORMATION, GUIDANCE, OR ADVICE PROVIDED BY THE AUTHORS OR IN THE REPOSITORY DOCUMENTATION SHALL CREATE ANY WARRANTY.

---

## 2. LIMITATION OF LIABILITY AND EXCLUSION OF DAMAGES

TO THE MAXIMUM EXTENT PERMITTED UNDER APPLICABLE LAW, IN NO EVENT SHALL THE AUTHORS, COPYRIGHT HOLDERS, OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE, CONSEQUENTIAL, OR COMPENSATORY DAMAGES WHATSOEVER (INCLUDING, WITHOUT LIMITATION, DAMAGES FOR LOSS OF PROFITS, REVENUE, DATA, REPUTATION, GOODWILL, WORK STOPPAGE, SYSTEM FAILURE OR MALFUNCTION, COMPUTER DAMAGE, BUSINESS INTERRUPTION, LOSS OF BUSINESS OPPORTUNITIES, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES, OR ANY OTHER PECUNIARY LOSS), ARISING OUT OF OR IN ANY WAY RELATED TO:
1. THE USE, MISUSE, INABILITY TO USE, OR RELIANCE UPON THE SOFTWARE;
2. ANY ACTIONS, COMMANDS, DELETIONS, COMMITS, PUSHES, FILE MUTATIONS, OR PROCESSES EXECUTED BY AUTONOMOUS OR SUB-AGENT WORKFLOWS (INCLUDING `omp`, SUBAGENTS, WORKPOOLS, OR SHELL SCRIPTS);
3. ANY DEFECT, ERROR, OMISSION, DELAY, MALFUNCTION, OR SECURITY VULNERABILITY IN THE SOFTWARE OR ITS ARTIFACTS;
4. ANY CHARGES, FEES, OR EXPENSES INCURRED FROM THIRD-PARTY LLM PROVIDERS, APIS, CLOUD PLATFORMS, OR COMPUTE SERVICES;
5. ANY UNAUTHORIZED ACCESS TO OR ALTERATION OF YOUR TRANSMISSIONS, DATA, SECRETS, CREDENTIALS, OR REPOSITORIES.

THIS LIMITATION APPLIES REGARDLESS OF THE THEORY OF LIABILITY, WHETHER BASED ON CONTRACT, TORT (INCLUDING NEGLIGENCE), STRICT LIABILITY, INDEMNITY, WARRANTY, BREACH OF STATUTORY DUTY, OR OTHERWISE, EVEN IF THE AUTHORS HAVE BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES, AND EVEN IF A LIMITED REMEDY FAILS OF ITS ESSENTIAL PURPOSE.

---

## 3. AUTONOMOUS AGENT EXECUTION AND ARBITRARY CODE EXECUTION RISKS

The Software utilizes autonomous multi-agent orchestration frameworks (such as Directed Acyclic Graph engines, subagent delegation via `task`, terminal execution via `bash`/`exec`, filesystem manipulation via `edit`/`write`, and git operations). 

**YOU ACKNOWLEDGE AND ASSUME ALL INHERENT RISKS ASSOCIATED WITH AUTONOMOUS AGENT EXECUTION:**
- **System and Filesystem Modifications**: Subagents and scripts may create, modify, overwrite, truncate, or permanently delete files, directories, symlinks, configuration files, and system registries.
- **Arbitrary Shell Execution**: The scripts and subagents may execute arbitrary shell commands, process pipelines, compilers, and test suites with the privileges of the active operating system user.
- **Git Repository Mutations**: Workflows may rewrite git history, commit changes, create branches, stage files, or push commits to remote repositories.
- **Network and Service Requests**: Agents may initiate outbound network connections, API requests, package downloads, and interactions with external endpoints.

**RECOMMENDED SAFEGUARDS**:
- **NEVER** run this Software with root, administrator, or elevated system privileges.
- Always execute the Software within an isolated, sandboxed environment (such as disposable Docker containers, virtual machines, or restricted execution jails) with strict read-only volume mounts and isolated networks where feasible.
- Maintain comprehensive, verified, out-of-band backups of all source code, databases, configuration files, and system states prior to invoking any orchestration workflow.
- Always review and inspect any proposed diffs, generated code, and automated execution logs before deploying changes to staging or production systems.

---

## 4. THIRD-PARTY LLM APIS, PROVIDER CHARGES & SERVICE TERMS

The Software is an orchestration engine designed to interact with third-party Large Language Model (LLM) Application Programming Interfaces (including but not limited to Anthropic Claude, Google Cloud / Gemini, OpenAI, xAI Grok, DeepSeek, and various API gateways).

- **Financial Responsibility**: Automated multi-agent workflows (especially multi-tiered panels, iterative falsification loops, and high-thinking models such as Claude Opus 5.5 xhigh or Gemini Pro Deep Think) may generate substantial token consumption, high concurrency, and rapid API usage. **You are solely and exclusively responsible for monitoring, managing, and paying all API charges, subscription fees, compute costs, and cloud infrastructure expenses incurred through your use of the Software.**
- **Third-Party Terms Compliance**: You are solely responsible for ensuring that your use of the Software complies with the respective Terms of Service, Acceptable Use Policies, Data Privacy Charters, and rate limits of each model provider and API platform you configure.
- **No Affiliation or Endorsement**: The Authors are independent entities and are not affiliated with, sponsored by, or endorsed by Anthropic, Google, OpenAI, GitHub, or any other commercial model vendor.

---

## 5. NO PROFESSIONAL, LEGAL, FINANCIAL, OR CERTIFIED AUDITING ADVICE

The Software contains role-playing personas and synthetic evaluation prompts, including but not limited to personas titled:
- `LaborEmploymentCounsel.json`
- `LaborLawComplianceAuditor.json`
- `EnterpriseSecurityArchitect.json`
- `FormalMethodsProfessor.json`
- `DatabasePerformanceAuditor.json`
- `CorrectnessContractFalsifier.json`
- `SecurityInvariantAuditor.json`
- `SystemicBlastRadiusSentinel.json`

**CRITICAL NOTICE REGARDING SIMULATED PERSONAS:**
- **NOT LEGAL ADVICE**: All outputs, reviews, guidelines, and annotations generated by "LaborEmploymentCounsel", "LaborLawComplianceAuditor", or any legal-themed persona are synthetically generated text produced by probabilistic machine learning models. They **DO NOT** constitute formal legal advice, legal counsel, legal opinions, statutory analysis, or formal compliance certification under any jurisdiction (including federal, state, EU, or international labor laws). No attorney-client relationship is formed or intended. Consult a licensed, qualified attorney in your jurisdiction for legal counsel.
- **NOT CERTIFIED SECURITY OR SAFETY AUDITING**: Outputs from security or verification personas do not constitute certified cybersecurity audits, penetration testing certifications, cryptographic guarantees, or compliance signoffs under formal safety standards (e.g., ISO 26262, DO-178C, IEC 61508, Common Criteria, SOC 2, HIPAA, PCI-DSS).
- **SIMULATED CONTRACTS & HEURISTIC FORMAL METHODS**: Implementations of SMT solving (via Z3), property fuzzing (via Hypothesis), and "Cryptographic Waiver Protocols" are algorithmic heuristics designed for developer assistance. They do not constitute formal mathematical proofs of total program correctness or absence of security vulnerabilities.

---

## 6. INTELLECTUAL PROPERTY, DATA PRIVACY & EXPORT COMPLIANCE

- **Your Responsibility for Input Data**: When providing source code, prompts, configurations, or proprietary documents to the Software, you represent and warrant that you possess all necessary rights, licenses, and permissions to submit such materials to third-party LLM providers.
- **Export Control Laws**: You agree to comply with all applicable export and re-export control laws and economic sanctions regulations, including the U.S. Export Administration Regulations (EAR), trade sanctions administered by the Office of Foreign Assets Control (OFAC), and equivalent local laws.
- **Data Privacy**: You are solely responsible for complying with relevant data privacy statutes (e.g., GDPR, CCPA, HIPAA) when processing personal, confidential, or regulated data through the Software.

---

## 7. USER INDEMNIFICATION

You agree to defend, indemnify, and hold harmless the Authors, contributors, repository owners, and any associated affiliates from and against any and all claims, actions, suits, demands, damages, obligations, losses, liabilities, costs, debts, and expenses (including reasonable attorneys' fees and litigation expenses) arising out of or related to:
1. Your access to or use of the Software;
2. Your violation of any provision of this Disclaimer or any applicable law, rule, or regulation;
3. Any content, code, or data provided by you or processed through your configured accounts;
4. Any damage or loss caused to your systems, repositories, data, or third-party platforms resulting from agent execution under your authority;
5. Any claims by third-party model providers, cloud hosts, or regulatory authorities concerning your usage.

---

## 8. SEVERABILITY & GOVERNING LAW

If any provision of this Disclaimer is found by a court of competent jurisdiction to be invalid, illegal, or unenforceable, such provision shall be severed or modified to the minimum extent necessary to make it valid and enforceable, and the remaining provisions shall continue in full force and effect.

---

**BY CONTINUING TO USE THIS REPOSITORY, YOU CERTIFY THAT YOU HAVE READ, UNDERSTOOD, AND VOLUNTARILY AGREED TO ALL TERMS, CONDITIONS, AND DISCLAIMERS ABOVE.**
