# from django.conf import settings
# from .models import Grading


# class GradingBox():
#     """
#     This is the base class for grading applicants in bulk
#     """
#     def __init__(self, request):
#         self.session = request.session
#         grading_box = self.session.get(settings.GRADING_SESSION_ID)
#         if settings.GRADING_SESSION_ID not in request.session:
#             grading_box = self.session[settings.GRADING_SESSION_ID] = {}
#         self.grading_box = grading_box


#     def addon(self, grading):
#         """
#         This function will add grading to session
#         This function will ONLY add grading marked for approval
#         """
#         grading_id = str(grading.id)
#         if grading_id in self.grading_box:
#             self.grading_box[grading_id]["vendor"] = grading
#         else:
#             self.grading_box[grading_id] = {'total_core': int(grading.total_marks)}
#         self.commit()

#     def remove(self, grading):
#         """
#         Delete item from grading_box
#         """
#         grading_id = str(grading.id)
#         if grading_id in self.grading_box:
#             del self.grading_box[grading_id]
#             self.commit()

#     def __iter__(self):
#         """
#         Collect the grading_ids in the session data to query the database
#         and return iterable gradings
#         """
#         grading_ids = self.grading_box.keys()
#         selected_grading = Grading.objects.filter(id__in=grading_ids)
#         grading_box = self.grading_box.copy()

#         for grading in selected_grading:
#             grading_box[str(grading.pk)]["vendor"] = grading

#         for applicant in grading_box.values():
#             applicant["total_marks"] = applicant["total_core"]
#             yield applicant


#     def __len__(self):
#         """
#         Get the grading_box data and count the items
#         """
#         return len(self.grading_box.values())

#     def commit(self):
#         self.session.modified = True

#     def clean_box(self):
#         del self.session[settings.GRADING_SESSION_ID]
#         self.commit()
