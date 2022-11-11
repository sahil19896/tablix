<!-- add-breadcrumbs -->
# Policy Document Management

This Document can be used for policy approval for HR, Finance, Sales. Approval should be only from TMT members.

To create new Policy Document Management go to:

> Desktop > In Search bar Search for Policy Document Management

<img class="screenshot" alt="Policy Document Management" src="/docs/assets/img/human-resources/policy_1.png">

> Desktop > Policy Document Management > New

<img class="screenshot" alt="Policy Document Management" src="/docs/assets/img/human-resources/policy_2.png">

<b>Docuemnt Overview :</b>

<img class="screenshot" alt="Policy Document Management" src="/docs/assets/img/human-resources/policy_3.png">

1. <b>Document Name</b>: is the Subject or Title of the document.

2. <b>Document Type</b>: is the type of document like Policy, Procedure or any workflow.

3. <b>Approval Date</b>: is the maximum approval date for <b>TMT</b> Members. 

4. <b>Policy Request By</b>: This field is automatically filled with the current USER ID as a Policy Requester.

5. <b>Notify</b>: If you want to repeat this document again after a perticular time interval then you can select this field as a frequency. This field is having three values <b>Weekly</b>, <b>Monthly</b> & <b>Quarterly</b>. 

	If you select Weekly then notifications, will be sent after 7 days to the <b>Policy Users</b>.
	If you select Monthly then notifications, will be sent on Monthly base to the <b>Policy Users</b>.
	If you select Quarterly then notifications, will be sent on Quarterly base to the <b>Policy Users</b>.

6. <b>Policy Approvers</b>: This table is automatically filled with the TMT Member list, but you can add as many as member as you want by clicking on Add Row after that select employee in the table.

7. <b>Policy Description</b>: here you can add the discription of the Policy. This is the mandatory field.

<b>Note: You can also upload images in description. the way to do this is, first fill all the details in form and save it. after that g
o to the description and click on Image button in desription bar. then you can brows and upload the images which you want. Only after saveing the document you can insert image in description.</b>

8. <b>Quiz</b>: In the table you can multiple choice questions for the users with choices and answers as well. Policy users can't see this table. This table is non-mandatory, if you don't want to add questions, you can leave this field as blank.

9. <b>Department</b>: This table is for Selection of employee on the bases of department. if you want to send the Policy for a perticular department then you can select the department here and according to that department list of the Employees are populated on next table <b>Policy Employee</b>. 

9. <b>All Employee</b>: If you click on this Check Box, all the employees are Populated in Policy Employee table.

10. <b>Policy Employee</b>: This table is for Policy Users like to whom you want to assign this Policy. This is the Mandatory table. you must need to enter Employee in this table before saving the form. 


<b>Working Process</b>: 
			For demo, TMT members are remove from Approval Table because a Notification goes to All the Member.

1. Once you enter all the details in form. then send the document for Approval from TMT Members. Click on the Action Button and then <b>Approval Request</b>. Now the status of the Document will be changed from OPEN to Waiting For Approval.

<img class="screenshot" alt="Policy Document Management" src="/docs/assets/img/human-resources/tablix_4.png">

2. If the <b>TMT</b> Members does not review the document or does not Approve or Decline the Document before approval date then on this date, two notification will be sent to the approver as a remainder for him.

3. In case if <b>TMT</b> Member does not approve the Document then after the Approval date, every hour a notification is sent to the approver, stating that, "Please complete the Task <b>Immediately</b>." This escalation notification also goes to <b>CEO</b> as a remainder for him that this approver does not review the Policy yet.

4. Now a notification goes to Approvers and TODO is created in the System. At this stage the document is freeze and no one will be able to make changes in the form.

<img class="screenshot" alt="Policy Document Management" src="/docs/assets/img/human-resources/tablix_5.png">

5. Approver can approve or decline the policy by clicking on Approve or Decline Button. If the approver decline the Policy then system will ask him about the reason for decline and record his reason in the from as well.

<img class="screenshot" alt="Policy Document Management" src="/docs/assets/img/human-resources/tablix_6.png">

<b>NOTE: Only TMT Members(Policy Approvers) can see the Approve & Decline button.</b>

<img class="screenshot" alt="Policy Document Management" src="/docs/assets/img/human-resources/tablix_7.png">

6. If the Any of the approver decline the document, the Document does not complete and again it come in Open stage. The decline check box is checked with the valid reason.

<img class="screenshot" alt="Policy Document Management" src="/docs/assets/img/human-resources/tablix_8.png">

7. Now the Document goes to Policy Requester queue. after necessary changes, again he sent the approval request. Now the document will goes to those particular apprver who reject the document. if the Approver approve the document, then the document will be complete and the status of the document become <b>Completed</b> and green.

<img class="screenshot" alt="Policy Document Management" src="/docs/assets/img/human-resources/tablix_9.png">

8. Now document comes under requester queue and he can submit the Document. Once he Click on Submit the Document Status become Approved and this document will assign to all the users which are selected for this policy.

<img class="screenshot" alt="Policy Document Management" src="/docs/assets/img/human-resources/tablix_10.png">

9. Policy Users can't see any content of the document directly untill they will click on the <b>Read Complete Document</b> button. once they click on the button, they will be redirected to document view page. 

<img class="screenshot" alt="Policy Document Management" src="/docs/assets/img/human-resources/tablix_11.png">

10. Here they can read the policy and submit their confirmation after reviewing they policy and Quiz as well.

<img class="screenshot" alt="Policy Document Management" src="/docs/assets/img/human-resources/tablix_12.png"> 


<b>Note: In Case if the Policy Users does not review the policy within the 24hr. after the document assign to them. Then 2 notification goes to them as reminder for first day. then next day after every hour a notifition goes to those user with HR and CEO as CC. tating that their task is pending in queue for long.</b>

11. once they read and confirm the document. automatically an entry made in their Employee detail form with Ref No. of document 
with confirm date. and also an email is shot with attaching PDF of the document for their reference.

<img class="screenshot" alt="Policy Document Management" src="/docs/assets/img/human-resources/tablix_13.png">

<img class="screenshot" alt="Policy Document Management" src="/docs/assets/img/human-resources/tablix_14.png">

<img class="screenshot" alt="Policy Document Management" src="/docs/assets/img/human-resources/tablix_15.png">

<img class="screenshot" alt="Policy Document Management" src="/docs/assets/img/human-resources/tablix_16.png">

<b>Note: The system will check the user signature present on his database or not. if signature is not present then system will ask to the user to upload their signature and if already present then system will bypass the signature upload process.</b>

<img class="screenshot" alt="Notification" src="/docs/assets/img/human-resources/noti_11.png">

<img class="screenshot" alt="Notification" src="/docs/assets/img/human-resources/noti_12.png">

<img class="screenshot" alt="Notification" src="/docs/assets/img/human-resources/noti_14.png">

{next}
