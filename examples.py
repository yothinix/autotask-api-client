from autotask import query, create


ticket = query(
    entity='Ticket',
    filter_field='ticketnumber',
    filter_value='T20180220.0001',
    select_fields=(
        'id', 'AccountID', 'CreateDate', 'DueDateTime',
        'TicketNumber', 'Title', 'Description', 'AssignedResourceID'
    )
)


resource = query(
    entity='Resource',
    filter_field='id',
    filter_value='29682885',
    select_fields=(
        'id', 'Email', 'FirstName', 'LastName',
        'ResourceType', 'Title', 'UserName'
    )
)

ticket_note = create(
    entity='TicketNote',
    update_object={
        'Description': 'Comment: "Great service as always!"',
        'NoteType': '1',
        'Publish': '1',
        'ticketID': '7872',
        'Title': 'Good rating from Cory Black'
    }
)


print('This is TICKET instance')
print('-----------------------')
print(ticket)
print('-----------------------')
print('This is RESOURCE instance')
print('-----------------------')
print(resource)
print('-----------------------')
