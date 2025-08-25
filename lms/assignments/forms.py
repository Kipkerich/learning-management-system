from django import forms
from .models import Assignment, Question, Choice, StudentAnswer

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'assignment_type', 'due_date', 'total_marks', 'is_published']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'marks', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 3}),
        }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text', 'is_correct']
        widgets = {
            'choice_text': forms.TextInput(attrs={'placeholder': 'Enter choice text'}),
        }

ChoiceFormSet = forms.inlineformset_factory(
    Question, Choice, form=ChoiceForm, extra=4, max_num=6, can_delete=True
)

class StudentAnswerForm(forms.ModelForm):
    class Meta:
        model = StudentAnswer
        fields = ['answer_text']

    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop('question', None)
        super().__init__(*args, **kwargs)
        
        if self.question and self.question.assignment.assignment_type == 'multiple_choice':
            # Add selected_choice field for multiple choice questions
            self.fields['selected_choice'] = forms.ModelChoiceField(
                queryset=Choice.objects.filter(question=self.question),
                widget=forms.RadioSelect,
                empty_label=None,
                required=False  # Make it not required initially
            )
            # Remove answer_text field for multiple choice
            del self.fields['answer_text']
        else:
            # For text input questions, remove selected_choice if it exists
            if 'selected_choice' in self.fields:
                del self.fields['selected_choice']
            
            # Make answer_text required for text input questions
            self.fields['answer_text'].required = True