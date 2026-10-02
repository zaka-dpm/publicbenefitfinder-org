"""Editorial guidance by service type, with source-specific fields added separately."""
import re

# These instructions explain the process without inventing payment amounts or approval guarantees.
PROFILES = {
 'snap': {
  'pattern':r'\bsnap\b|calfresh|food stamps|3squares|basic food|food assistance',
  'benefit':'Food assistance helps an eligible household buy groceries. The household’s award and reporting obligations are explained in the agency’s decision notice. Keep the application process separate from EBT card service: an application office and a card replacement line may have different contact details.',
  'prepare':'Identify who lives with you and who buys and prepares meals together. Record income and expenses before starting the form so you can answer consistently. Tell the office about an immediate lack of food; do not assume that an ordinary processing period is the only option.',
  'after':'Read requests for evidence and the eligibility decision. Keep a copy of the application, submission receipt and notices. Once approved, follow the reporting and renewal instructions for your household. If you disagree with a decision, use the appeal instructions in the notice.',
  'faqs':[
   ('Can a working household apply?','Having a job does not by itself settle SNAP eligibility. The office reviews income, household circumstances and other program rules.'),
   ('What if I need food before the decision?','Explain your immediate circumstances to the application office and ask about expedited processing. For food available sooner, contact a local food pantry or 211.'),
   ('Do I have to complete an interview?','Follow the agency’s application instructions and any interview notice. An online form may be only the first part of the process.'),
   ('How much will my household receive?','Use the agency’s current income and benefit guidance. Your approval notice gives the amount for your case; a maximum shown in a table is not a guaranteed award.')]
 },
 'wic': {
  'pattern':r'\bwic\b',
  'benefit':'WIC combines supplemental food benefits with nutrition support. It is a separate program from SNAP. A clinic explains the food package, nutrition services and the benefit card or other purchasing method used locally.',
  'prepare':'Contact a local WIC clinic before visiting. Explain who you want to enroll and ask who must attend the assessment. If you already receive another benefit, ask whether its enrollment record can be used for the income check.',
  'after':'Keep the clinic’s follow-up appointment and certification information. Ask how to report changes, use your food benefits and get breastfeeding or nutrition support. Card problems and appointment questions may go to different contacts.',
  'faqs':[
   ('Is WIC the same as SNAP?','No. WIC has its own eligibility assessment, nutrition services and food package. Ask the clinic about WIC even if your household already receives SNAP.'),
   ('Can someone caring for a child arrange the visit?','Tell the clinic that you are the parent, guardian or caretaker and ask which records and permissions it needs for the child’s appointment.'),
   ('Why is there a clinic assessment?','The appointment lets staff check eligibility and nutritional needs. Ask what the assessment involves and whether the applicant must attend.'),
   ('Does WIC cover every grocery purchase?','WIC food benefits are for approved items in the participant’s food package. The clinic or program website explains the approved foods and shopping rules.')]
 },
 'referral': {
  'pattern':r'211|2-1-1',
  'benefit':'A referral service helps you locate organizations providing food, housing, utility help and other support. It connects you with providers rather than approving a benefit or paying a bill itself.',
  'prepare':'Give your city or ZIP code and explain the help you need. Mention a shutoff, eviction or other deadline. Ask which provider serves your address, whether intake is open and what you should prepare before calling.',
  'after':'Contact each referred organization and record its answer. If it cannot help, return to the referral service with that information and ask about another provider. Funding and intake availability can change.',
  'faqs':[
   ('Will a referral pay my bill?','A referral alone does not pay a bill. The organization you contact checks eligibility, funding and the services it can provide.'),
   ('What should I have ready for the conversation?','Your location, a description of the need and any urgent deadline help the specialist find relevant services. Have a way to save contact details.'),
   ('Can I ask about more than one problem?','Describe the needs affecting your household together, such as food and utilities. Different providers may handle each request.'),
   ('What if the first provider cannot help?','Tell the referral service what happened. Ask for alternatives rather than assuming one unsuccessful referral means no help exists.')]
 },
 'weatherization': {
  'pattern':r'weatherization',
  'benefit':'Weatherization improves an eligible home’s energy efficiency. An assessment determines which measures can be offered. It is different from help paying an overdue utility bill, and it does not mean every requested home repair will be covered.',
  'prepare':'Find the provider serving your address. Ask about income verification, the waiting list, an assessment and any permissions needed for a rented home. Explain safety concerns and whether anyone in the household has special access needs.',
  'after':'Keep the provider’s appointment instructions and allow access for approved inspections or work. Ask which measures were authorized and who to contact about follow-up issues. For an urgent bill or shutoff, seek utility assistance separately.',
  'faqs':[
   ('Does weatherization pay my energy bill?','Weatherization is focused on approved work to the home. Ask about a separate energy assistance program if the immediate problem is an unpaid bill.'),
   ('Can a renter ask about the program?','Contact the local provider. Rental properties may need owner permission and must meet the program’s requirements.'),
   ('Can I choose any repairs?','The provider’s assessment and program rules determine the eligible work. Approval is not a promise to cover a general renovation.'),
   ('Will work start immediately?','Ask about intake and scheduling. Provider capacity, assessments and a waiting list can affect when work begins.')]
 },
 'energy': {
  'pattern':r'liheap|energy|utility|utilities|heating|pipp|care.fera|crisis fuel|crisis intervention',
  'benefit':'Energy assistance can take different forms: a bill payment, an ongoing discount, a payment arrangement or help during a heating or cooling emergency. Check which service this program offers and whether it covers your utility or fuel.',
  'prepare':'Gather the latest bill and any disconnection or fuel notice. Identify the account holder and the people living at the address. For an emergency, explain the deadline to the provider and contact the utility about available arrangements while the request is reviewed.',
  'after':'Keep the intake confirmation and respond to requests. Ask whether support is paid to the supplier and whether you still owe part of the balance. Do not assume that submitting an application automatically prevents disconnection.',
  'faqs':[
   ('Does applying stop a shutoff?','Do not rely on the application alone. Contact your utility and the assistance provider about the notice, deadline and any available protection or arrangement.'),
   ('Can this cover the whole bill?','The provider decides the assistance available under its rules and funding. Ask which charges are covered and what balance you remain responsible for.'),
   ('Is emergency help handled differently?','Tell the provider about a disconnection, an empty fuel supply or another immediate heating or cooling problem. Ask which emergency intake process applies.'),
   ('Can I get help reducing future bills?','Ask about ongoing discounts and weatherization as well as bill payment help. These services have separate requirements and application steps.')]
 },
 'unemployment': {
  'pattern':r'unemployment|edd',
  'benefit':'Unemployment insurance provides temporary income after a qualifying loss of work. The agency reviews wages and the circumstances of separation; a claim is not automatically approved because a person is unemployed.',
  'prepare':'Gather employer names, work dates and earnings information. Explain accurately why each job ended or hours were reduced. Use the state’s claim system and read the directions for continuing certifications, work search and reporting new earnings.',
  'after':'Watch for requests about wages or separation and submit continuing certifications as instructed. Report work and income accurately, including part-time work. If benefits are denied, use the appeal deadline and instructions in the determination.',
  'faqs':[
   ('Does filing the first claim guarantee payment?','No. The agency must make an eligibility determination. Complete the initial claim and follow any continuing certification instructions.'),
   ('What if I work part time?','Report work and earnings according to the state’s instructions. The agency decides how the work affects your claim.'),
   ('What if my work was in another state?','Tell the unemployment agency where you worked. Ask which state should handle the claim before submitting duplicate applications.'),
   ('How do I challenge a denial?','Read the determination for the appeal method and deadline. Keep the notice and records supporting your account of the work separation.')]
 },
 'tax': {
  'pattern':r'tax|eitc|vita|earned.income.credit|working.family.credit|kids.credit|homestead.credit|grocery.credit|homeowner.renter.credit',
  'benefit':'A tax credit is claimed through the applicable tax return or claim form. The calculation can depend on the tax year, income, residency and dependents. Refundability and eligibility are separate questions: a refundable credit still has qualifying rules.',
  'prepare':'Choose the tax year you are filing before checking a threshold or form. Gather income statements, dependent information and any housing records needed for this particular credit. Use the revenue agency’s instructions for that year.',
  'after':'Save the filed return, worksheets and supporting records. Respond to any revenue agency request and check refund status through the agency’s own system. If you need filing assistance, look for a qualified free preparation service.',
  'faqs':[
   ('Does the tax year matter?','Yes. Eligibility, amounts and forms can change between years. Use the instructions for the year of the return or claim you are filing.'),
   ('Do I need to file to claim it?','Follow the revenue agency’s claim instructions. A credit is not normally issued just because you meet an income guideline; the required return or claim must be submitted.'),
   ('What does refundable mean?','A refundable credit can produce a refund beyond the tax owed, if you qualify. Check whether this specific credit is refundable and how it is calculated.'),
   ('Where can I get help filing?','Check the agency’s free tax help information or ask 211 about a nearby VITA or other qualified preparation service. Confirm the documents and appointment requirements.')]
 },
 'childcare': {
  'pattern':r'child.?care',
  'benefit':'Child care assistance helps eligible households with approved care costs. Check the provider rules, covered hours and any family contribution before committing to a care arrangement.',
  'prepare':'Explain the activity for which care is needed, such as work or school. Gather the child’s details, household income and schedule, and ask whether the intended provider participates. Check whether intake is open or a waiting list applies.',
  'after':'Keep the authorization and provider information. Ask how to report changes in work, school, household circumstances or care arrangements. Confirm covered dates and any amount you owe before starting care.',
  'faqs':[
   ('Can I choose a child care provider?','Ask the program which providers can be approved. Choosing a provider does not automatically make that care eligible for payment.'),
   ('Will every hour of care be covered?','Check the authorization for covered hours and dates. The approved schedule may depend on the reason care is needed.'),
   ('Could my family have a contribution?','Ask about any copayment or other family responsibility before agreeing to care. Costs depend on the program’s rules and your circumstances.'),
   ('What changes should I report?','Use the program’s reporting instructions for changes to household income, work or school, and your child’s provider or schedule.')]
 },
 'health': {
  'pattern':r'medicaid|medicare|chip|kidscare|kidcare|peachcare|medi-cal|ahcccs|health|medical|clinica|covered.california',
  'benefit':'Health programs have different eligibility pathways and coverage rules. Public insurance, a marketplace plan and a clinic service are different forms of help. Confirm the coverage or service offered by this program, including provider participation and any costs.',
  'prepare':'Identify each person seeking coverage, their existing insurance and the eligibility pathway relevant to them. Gather requested income and identity information. Ask for application help if household members have different needs or coverage situations.',
  'after':'Read the eligibility notice, coverage start date and any plan-selection instructions. Check that the health provider you want to use participates. Keep contact details current and respond to renewal requests or notices about changes.',
  'faqs':[
   ('Does a decision for one family member decide everyone’s case?','Do not assume so. Household members can have different eligibility pathways, especially adults and children. Ask the program to assess each applicant.'),
   ('Does an application mean I can use coverage immediately?','Check the decision notice for approval, coverage dates and any enrollment steps. A submitted form is not proof that a particular service is covered.'),
   ('How do I check whether my doctor is included?','Use the program or plan’s provider information and confirm with the provider before arranging care. Participation can vary by plan.'),
   ('What if I receive a renewal notice?','Follow the notice and return the requested information by its deadline. Ask the program for help if the instructions are unclear.')]
 },
 'legal': {
  'pattern':r'legal|courts.*eviction',
  'benefit':'Legal aid and court self-help services can explain options for eligible civil problems. Information, advice and representation are different levels of service. Ask what this provider can offer for your issue and service area.',
  'prepare':'State the legal issue and give the date of any hearing, eviction notice or response deadline. Keep court papers, notices and relevant correspondence together. Use the provider’s intake process rather than waiting for a general benefit application to resolve a legal deadline.',
  'after':'Follow the provider’s instructions and keep copies of papers you submit. Ask clearly whether the provider has agreed to represent you. A request for help alone does not extend a court deadline.',
  'faqs':[
   ('Does contacting legal aid mean I have a lawyer?','No. Ask whether your request has been accepted for advice or representation. A completed intake is not the same as an agreement to represent you.'),
   ('Should I mention a hearing or eviction deadline?','Yes. Give the exact date and bring the notice or court papers. A deadline can affect how the provider handles intake.'),
   ('Can this provider help with any legal case?','Providers have service areas and limits on the cases they handle. Ask about your particular issue and request a referral if it is outside their scope.'),
   ('What if representation is not available?','Ask about self-help information, court assistance or another provider. Continue to track deadlines while seeking help.')]
 },
 'cash': {
  'pattern':r'tanf|cash|temporary.assistance|temporary.disability|calworks|family.investment|general.assistance|senior.benefits|\bssi\b',
  'benefit':'Cash assistance is awarded under the program’s household, income and other eligibility rules. The approval notice explains the payment, its delivery and any continuing requirements. Other assistance, such as food or health coverage, may need a separate assessment.',
  'prepare':'Identify the people applying and gather household income and any requested resource information. Explain child or dependent care and circumstances affecting work or other requirements. Ask about exemptions rather than assuming a requirement applies in the same way to everyone.',
  'after':'Read the payment and reporting instructions. Keep appointments and respond to review requests. Ask the office how a change in work, income or household members affects the case, and use the notice’s appeal instructions if you disagree with a decision.',
  'faqs':[
   ('Is the payment the same for every household?','No. The program’s rules and eligibility calculation determine an approved household’s payment. Use current agency guidance and your decision notice.'),
   ('Are there continuing requirements?','Ask the office about reporting, reviews and any work, training or other obligations that apply to your case, including possible exemptions.'),
   ('Can I ask about food and health help too?','Yes. Ask whether the office can assess those programs or direct you to their applications. Approval for cash assistance does not automatically settle every other benefit.'),
   ('What if my application is denied?','Read the notice for the reason and appeal process. Keep the records you submitted and respond within the stated deadlines.')]
 },
 'housing': {
  'pattern':r'housing|raft|shelter|navigation.center|mission.at.kern|open.door.network',
  'benefit':'Housing resources may offer emergency support, shelter, rental assistance or housing counseling. These are different services with different intake rules. Check the help available through this provider and whether a waiting list or referral is required.',
  'prepare':'Explain your current housing situation and any notice or deadline. Gather tenancy or housing records and evidence of the need. Ask whether a landlord, property owner or another organization must also complete part of the process.',
  'after':'Keep intake and case contact details, and respond to requests. Confirm any payment, placement or agreement before relying on it. If there is a court deadline, seek legal help as well as housing assistance.',
  'faqs':[
   ('Does applying guarantee housing or a payment?','No. The provider assesses the request, eligibility and availability. Confirm what has actually been approved and any remaining steps.'),
   ('Do I need to tell my landlord?','Ask the program whether landlord or owner participation is needed. Some assistance processes require information from both the household and property owner.'),
   ('What if I have an eviction notice?','Give the provider the notice and deadline. Contact legal aid or court self-help too; a housing assistance request does not automatically change court dates.'),
   ('What if intake is closed?','Ask about the next opening, a waiting list and other local providers. For urgent local referrals, contact 211.')]
 },
 'foodbank': {
  'pattern':r'food.bank|gleaners|feeding.america|food.pantry',
  'benefit':'Food banks and partner pantries help people obtain food locally. A food bank may distribute through partner organizations rather than offer walk-in service at its main address.',
  'prepare':'Find a distribution or pantry serving your location. Check the hours, appointment rules and any information needed before travelling. Explain household needs and ask about accessibility or dietary concerns.',
  'after':'Follow the local distribution instructions and ask when you may return. If you need longer-term grocery support, explore SNAP or other nutrition programs separately.',
  'faqs':[
   ('Can I visit the food bank’s main address?','Check first. The organization may direct people to partner pantries or distribution sites instead of providing food at its warehouse.'),
   ('Do I need an appointment?','Ask the local distribution site. Hours, appointments and intake requirements vary between providers.'),
   ('Can I ask about dietary needs?','Tell the provider about the household’s needs. It can explain available food and any relevant services; particular items are not guaranteed.'),
   ('Is this a SNAP application?','No. Food distribution and SNAP are separate services. Ask for a SNAP referral if your household needs ongoing grocery benefits.')]
 },
 'veterans': {
  'pattern':r'veteran|\bva.benefits',
  'benefit':'Veteran resources can help with benefit claims, service records and referrals. Different VA benefits have different eligibility rules; a local service office may provide assistance with a claim rather than pay the benefit itself.',
  'prepare':'Explain whether the request concerns health care, compensation, pension, housing or another benefit. Gather service records and the notices or evidence relevant to that request. Ask who can help as an accredited representative.',
  'after':'Keep copies and claim or referral details. Respond to evidence requests and use the decision’s review or appeal instructions. Confirm the status with the agency handling the claim.',
  'faqs':[
   ('Does this office pay the benefit?','Ask which agency handles the benefit. A veteran service office may help prepare or track a claim while another agency makes the decision.'),
   ('What service records should I gather?','Ask for the checklist for your claim. Discharge information and records supporting the specific benefit request can be important.'),
   ('Can someone help with my claim?','Ask about accredited representation or the assistance offered by this office. Confirm what the representative can do for your request.'),
   ('What if I disagree with a decision?','Use the review or appeal instructions in the decision notice. Keep the notice and the evidence you provided.')]
 },
 'navigation': {
  'pattern':r'benefit.finder|sc.thrive|community.action|aging.*adult|outreach|catholic.charities|salvation.army|crisis.control|township|emergency.relief',
  'benefit':'This resource helps connect households with assistance or provides local services. Its programs can have different eligibility rules, coverage areas and funding. Ask about the specific service you need rather than assuming one intake covers every program.',
  'prepare':'Explain your location, the help needed and any immediate deadline. Ask whether you apply with this organization or a separate agency, and whether an appointment or referral is required.',
  'after':'Save the referral or application details. Complete any separate provider applications and contact the organization if the referral cannot help. The agency administering a benefit makes its eligibility decision.',
  'faqs':[
   ('Does a screening result approve benefits?','No. A screening or referral is a starting point. The organization administering the service or benefit makes its own decision.'),
   ('Can I ask about several needs?','Describe the household’s situation and ask which services are available. Separate applications or provider referrals may be needed.'),
   ('Who should receive my documents?','Confirm the application route and document checklist. Provide requested personal records directly through the provider’s stated process.'),
   ('What if the organization cannot help?','Ask for another local provider or a referral service. Availability and funding can change, so check intake before travelling.')]
 },
 'lifeline': {
  'pattern':r'lifeline.*phone',
  'benefit':'Lifeline reduces the cost of eligible phone or internet service through a participating company. Qualification and service enrollment are separate steps. Check the current discount and provider options through Lifeline Support.',
  'prepare':'Check the income or qualifying-program route that applies to you. Follow the application process for your state, provide evidence if requested, and identify the household according to the program’s rules.',
  'after':'After qualification, enroll with a participating service company. Read renewal or recertification notices and respond by their deadlines. Contact Lifeline Support and the provider if the discount is missing.',
  'faqs':[
   ('Does approval automatically start the discount?','You also need eligible service with a participating company. Follow both the qualification and provider enrollment steps.'),
   ('Is this the former Affordable Connectivity Program?','No. Lifeline and ACP are different programs. Use Lifeline’s current instructions rather than an old ACP offer.'),
   ('What if someone else at my address receives Lifeline?','Check the household definition and worksheet. An address alone does not describe whether people share income and expenses.'),
   ('What if the discount stops?','Check provider and recertification notices, then contact Lifeline Support about the reason and the steps available.')]
 },
 'property': {
  'pattern':r'missingmoney|unclaimed.property',
  'benefit':'An unclaimed property search helps you locate assets reported to participating state programs. It is a search for property that may belong to you, rather than a new assistance payment.',
  'prepare':'Search names you have used and states where you lived or worked. A possible match still needs verification through the state’s claim process. Gather evidence connecting you to the owner or account.',
  'after':'Submit a claim through the responsible state program and follow its evidence requests. For an inherited claim, ask about the estate or relationship records required.',
  'faqs':[
   ('Does a search result prove the property is mine?','No. Check the details and follow the state’s ownership verification process.'),
   ('Should I search a state where I no longer live?','Yes, previous locations can be relevant. Search your history and follow the state program identified with a possible match.'),
   ('Can I ask about property belonging to a deceased relative?','Ask the state about its process for heirs or estates and the documents required. A name match does not establish a right to claim.'),
   ('Is this a benefits application?','No. It is a property search and claim process. Public assistance programs have separate applications.')]
 },
 'employment': {
  'pattern':r'job.center',
  'benefit':'Employment centers help people explore job search, workforce services and training opportunities. Some services are widely available, while a funded training program can have separate eligibility and enrollment rules.',
  'prepare':'Contact the center serving your location. Explain your employment goals, work history and any need for training or support. Ask about appointments, workshops and the information needed for a specific program.',
  'after':'Follow the plan or referral you agree with the center. Keep appointment details and ask how to access additional help if your circumstances change.',
  'faqs':[
   ('Does visiting guarantee a job?','No. The center offers employment services; employers make hiring decisions.'),
   ('Is every training course funded?','Ask about the specific course and funding program. Eligibility and approval may be required before costs are covered.'),
   ('Should I bring a resume?','Ask the center’s intake requirements. Your work and education history helps staff discuss appropriate services.'),
   ('Is this an unemployment claim?','Job services and unemployment insurance are separate. Use the state unemployment agency for a benefit claim.')]
 },
 'crisis': {
  'pattern':r'^988',
  'benefit':'988 connects people experiencing emotional distress or a mental health, substance use or suicide crisis with support. It is separate from a benefits or bill-assistance referral service.',
  'prepare':'Call or text 988, or use the chat service at the Lifeline website. Describe what you want help with at your own pace. If there is immediate physical danger or a medical emergency, call 911.',
  'after':'Discuss next steps and available support with the counselor. For food, housing or utility referrals, use 211 or the relevant local assistance provider separately.',
  'faqs':[
   ('Can I text instead of calling?','Yes. Use 988 by call or text, or follow the chat option on the Lifeline website.'),
   ('Must I be thinking about suicide to contact 988?','No. The service also supports people dealing with emotional distress and mental health or substance use crises.'),
   ('Can I contact the service about someone else?','You can ask for support when concerned about another person. Explain the circumstances to the counselor.'),
   ('Is 988 for rent or utility assistance?','For practical local assistance referrals, contact 211. Use 988 for emotional or crisis support.')]
 }
}

PROFILES.update({
 'clinic': {
  'pattern':r'clinica sierra|kern medical|omni family',
  'benefit':'This provider delivers health care rather than issuing health insurance benefits. Available appointments, services, insurance acceptance and charges depend on the clinic and the care requested.',
  'prepare':'Find a location offering the service you need and contact its appointment team. Explain whether you are a new patient and ask about insurance, payment assistance and records to bring.',
  'after':'Follow the care team’s appointment, prescription and referral instructions. Ask the billing team about charges separately from questions about treatment or insurance enrollment.',
  'faqs':[
   ('Is this an insurance application?','No. Arranging care with a clinic is separate from applying for Medicaid or marketplace coverage. Ask whether enrollment assistance is available.'),
   ('What if I do not have insurance?','Contact the clinic before the visit and ask about its current payment options and financial assistance process.'),
   ('Does every location offer the same services?','Check the service and appointment availability at the location you intend to visit.'),
   ('What should I bring?','Ask the appointment team about identification, insurance information, medications and relevant medical records.')]
 },
 'taxprep': {
  'pattern':r'vita|free tax preparation',
  'benefit':'Volunteer tax preparation helps qualifying taxpayers prepare and file a return. It is a service, not a separate tax credit or a promise of a refund.',
  'prepare':'Check current appointment availability, income and return-complexity limits. Ask about identification, taxpayer numbers, income statements and any joint-filing attendance requirements.',
  'after':'Review the completed return before authorizing filing. Keep a copy and the submission confirmation. Use the tax agency’s refund tracking service for refund questions.',
  'faqs':[
   ('Does this guarantee a refund?','No. The completed return determines whether tax is due or a refund is available.'),
   ('Can volunteers prepare every type of return?','Ask which situations the site can handle. Some business, investment or other complex returns may be outside its scope.'),
   ('Do I need an appointment?','Check the site’s current season and appointment instructions before visiting.'),
   ('Which tax year can I file?','Ask whether the site handles only the current filing season or also prior-year returns.')]
 },
 'marketplace': {
  'pattern':r'healthcare\.gov|health insurance marketplace',
  'benefit':'The health insurance marketplace lets applicants compare coverage and apply for available help with insurance costs. A plan has its own premium, covered services, provider network and cost-sharing rules.',
  'prepare':'Use the marketplace serving your state. Check enrollment dates or whether a qualifying life event allows enrollment now. Prepare household and expected annual income information.',
  'after':'Review the eligibility notice, choose a plan where required and follow the insurer’s payment instructions. Keep household and income information updated through the marketplace.',
  'faqs':[
   ('Is an application the same as active coverage?','Read the enrollment notice and insurer’s instructions. Plan selection, an effective date and any required first payment are separate steps.'),
   ('Can I enroll at any time?','Check open enrollment and special enrollment rules for the marketplace serving your state.'),
   ('How do I compare plans?','Compare premiums, deductibles, covered medicines and the network for your doctors as well as any available financial assistance.'),
   ('What if my income changes?','Report changes through the marketplace and read the updated eligibility notice.')]
 },
 'counseling': {
  'pattern':r'housing counseling|hud-approved',
  'benefit':'A housing counselor helps review housing options, costs and next steps. Counseling is separate from a rental assistance award, a mortgage approval or direct payment of arrears.',
  'prepare':'Find a counselor offering help with your specific concern. Ask about appointment methods and fees, then prepare housing costs, income information and notices relevant to the problem.',
  'after':'Keep the action plan and follow up with the lender, landlord or assistance program named in it. A counseling appointment does not automatically pause a foreclosure or eviction deadline.',
  'faqs':[
   ('Will counseling pay my rent or mortgage?','Counseling helps you understand options. Ask separately about programs that provide financial assistance.'),
   ('Is every service free?','Ask the counselor about fees for the particular service before booking.'),
   ('What if I have an urgent notice?','Tell the counselor the deadline and seek legal help for an eviction or foreclosure case when needed.'),
   ('Can I ask about buying a home?','Check whether the agency offers homebuyer education or pre-purchase counseling for your situation.')]
 }
})

# Match specific services before broader words such as health, housing or income.
ORDER=['clinic','taxprep','marketplace','counseling','crisis','lifeline','property','employment','wic','referral','weatherization','tax','childcare','foodbank','veterans','snap','unemployment','legal','cash','energy','housing','health','navigation']

def choose(title):
 for key in ORDER:
  if re.search(PROFILES[key]['pattern'], title, re.I): return key,PROFILES[key]
 raise ValueError('No editorial profile for '+title)
