# Autotask API Client

This is a proof of concept of using Autotask SOAP API in Python

## Requirement
* In order to use Pipfile, you need to install pipenv on your system
* You need to add .env file in the project directory in order to make it work. The example of env are shown below

```
AUTOTASK_USERNAME=banana@apple.com
AUTOTASK_PASSWORD=password
```

## Making Request
### Making Query
To query you need to specify Entity you want to query, A field for filter and it's value. You also need to specify a list of return field otherwise it will return `None`
```python
from autotask import Autotask


client = Autotask()
client.username = '<username>'
client.password = '<password>'

ticket = client.query(
    entity='Ticket',
    filter_field='ticketnumber',
    filter_value='T20180220.0001',
    select_fields=(
        'id', 'AccountID', 'CreateDate', 'DueDateTime',
        'TicketNumber', 'Title', 'Description', 'AssignedResourceID'
    )
)
```

The wrapper is equivalent to this XML body
```xml
<env:Envelope
	xmlns:xsd="http://www.w3.org/2001/XMLSchema"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xmlns:tns="http://autotask.net/ATWS/v1_5/"
	xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
	<env:Body>
		<tns:query
			xmlns="http://autotask.net/ATWS/v1_5/">
			<sXML>
				<![CDATA[
          <queryxml>
            <entity>Ticket</entity>
            <query>
              <field>ticketnumber
                <expression op="equals">T20180220.0001</expression>
              </field>
            </query>
          </queryxml>]]>
			</sXML>
		</tns:query>
	</env:Body>
</env:Envelope>
```


### Create Ticket Note
To create entity you need to specify Entity you want to create, A dictionary of update object. You also need to specify a list of return field otherwise it will return `None`
```python
from autotask import Autotask


client = Autotask()
client.username = '<username>'
client.password = '<password>'

ticket_note = client.create(
    entity='TicketNote',
    update_object={
        'Description': 'Comment: "Great service as always!"'
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
```

The wrapper is equivalent to this XML body
```xml
<?xml version="1.0" encoding="utf-16"?>
<soap:Envelope
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xmlns:xsd="http://www.w3.org/2001/XMLSchema"
	xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
	<soap:Body>
		<create
			xmlns="http://autotask.net/ATWS/v1_5/">
			<Entities>
				<Entity xsi:type="TicketNote">
					<Description>Comment: "Great service as always! !!!"</Description>
					<NoteType>1</NoteType>
					<Publish>1</Publish>
					<TicketID>7872</TicketID>
					<Title>Good rating from Cory Black</Title>
				</Entity>
			</Entities>
		</create>
	</soap:Body>
</soap:Envelope>
```

### Update User-Defined Fields on Ticket Entity
To update User-Defined Fields, You need to specify target Entity and lookup_keys in dictionary format. Then, you need to specified User-Defined Fields Name and value. Lastly, You also need to specify a list of return field otherwise it will return `None`
```python
from autotask import Autotask


client = Autotask()
client.username = '<username>'
client.password = '<password>'

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
```

The wrapper is equivalent to this XML body
```xml
<?xml version="1.0" encoding="utf-16"?>
<soap:Envelope
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <update xmlns="http://autotask.net/ATWS/v1_5/">
      <Entities>
        <Entity xsi:type="Ticket">
          <id>7872</id>
          <Title>This is Man test ticket</Title>
          <Status>1</Status>
          <Priority>1</Priority>
          <DueDateTime>2018-02-21T01:38:00</DueDateTime>
          <AccountID>0</AccountID>
          <AssignedResourceID xsi:type="xsd:int">29682885</AssignedResourceID>
          <AssignedResourceRoleID xsi:type="xsd:int">29683436</AssignedResourceRoleID>

					<UserDefinedFields>
					  <UserDefinedField>
					    <Name>Satisfaction</Name>
					    <Value>3</Value>
					  </UserDefinedField>
					</UserDefinedFields>

        </Entity>
      </Entities>
    </update>
  </soap:Body>
</soap:Envelope>
```


## Development
* To execute the test, running
```
pipenv run test
```

