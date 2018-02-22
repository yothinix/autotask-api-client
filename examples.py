import os

from autotask import Autotask


client = Autotask()
client.username = os.environ.get('AUTOTASK_USERNAME')
client.password = os.environ.get('AUTOTASK_PASSWORD')

ticket = client.query(
    entity='Ticket',
    filter_field='ticketnumber',
    filter_value='T20180220.0001',
    select_fields=(
        'id', 'AccountID', 'CreateDate', 'DueDateTime',
        'TicketNumber', 'Title', 'Description', 'AssignedResourceID'
    )
)

print('This is TICKET instance')
print('-----------------------')
print(ticket)
print('-----------------------')


resource = client.query(
    entity='Resource',
    filter_field='id',
    filter_value='29682885',
    select_fields=(
        'id', 'Email', 'FirstName', 'LastName',
        'ResourceType', 'Title', 'UserName'
    )
)

print('This is RESOURCE instance')
print('-----------------------')
print(resource)
print('-----------------------')


ticket_note = client.create(
    entity='TicketNote',
    update_object={
        'Description': 'Comment: "Great service as always! !!!!"',
        'NoteType': '1',
        'Publish': '1',
        'TicketID': '7872',
        'Title': 'Good rating from Cory Black'
    },
    select_fields=(
        'id', 'CreatorResourceID', 'Description', 'LastActivityDate',
        'NoteType', 'Publish', 'TicketID', 'Title'
    )
)

print('This is TICKET NOTE instance')
print('-----------------------')
print(ticket_note)
print('-----------------------')


update_ticket_satisfaction = client.update_udf(
    entity='Ticket',
    lookup_keys={
        'id': '7872',
        'Title': 'This is Man test ticket',
        'Status': '1',
        'Priority': '1',
        'DueDateTime': '2018-02-21T01:38:00',
        'AccountID': '0',
        'AssignedResourceID': '29682885',
        'AssignedResourceRoleID': '29683436'
    },
    field='Satisfaction',
    value='1',
    select_fields=(
        'id', 'AccountID', 'CreateDate', 'DueDateTime',
        'TicketNumber', 'Title', 'Description', 'AssignedResourceID'
    )
)


print('This is TICKET instance')
print('-----------------------')
print(update_ticket_satisfaction)
print('-----------------------')
