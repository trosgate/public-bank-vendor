from import_export import resources
from import_export.fields import Field
from tickets.models import Ticket


class TicketResource(resources.ModelResource):
    category = Field()
    status = Field()
    branch = Field()
    terminal = Field()
    created_by = Field()
    checklist = Field()
    sla_exception = Field()
    team = Field()
    engineer = Field()

    class Meta:
        model = Ticket
        fields = (
            'reference', 'terminal', 'created_by', 'title', 'status', 
            'category', 'branch','remarks', 'remarks_date',
            'team', 'created_at', 'arrival_time', 
            'engineer', 'checklist', 'sla_exception'
        )
        export_order = fields

    def dehydrate_branch(self, obj):
        return obj.branch.name

    def dehydrate_terminal(self, obj):
        return obj.terminal.name

    def dehydrate_category(self, obj):
        return obj.category.name

    def dehydrate_created_by(self, obj):
        return obj.created_by.get_full_name()

    def dehydrate_status(self, obj):
        return obj.get_status_display()

    def dehydrate_team(self, obj):
        return obj.team.title

    def dehydrate_checklist(self, obj):
        data = [x.item for x in obj.checklist.all()]
        checklist = ', '.join(data)
        return checklist

    def dehydrate_sla_exception(self, obj):
        data = [x.name for x in obj.sla_exception.all()]
        sla = ', '.join(data)
        return sla

    def dehydrate_engineer(self, obj):
        data = [x.assignee.get_full_name() for x in obj.engineer]
        sla = ', '.join(data)
        return sla
























