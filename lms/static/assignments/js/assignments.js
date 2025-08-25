// assignments/static/assignments/js/assignments.js

class AssignmentManager {
    constructor() {
        this.initAssignmentTaking();
        this.initAssignmentGrading();
    }

    initAssignmentTaking() {
        const takeAssignmentForm = document.getElementById('assignmentForm');
        if (takeAssignmentForm) {
            this.setupAssignmentValidation(takeAssignmentForm);
        }
    }

    setupAssignmentValidation(form) {
        const questionCards = document.querySelectorAll('.question-card');
        const isMultipleChoice = this.isMultipleChoiceAssignment();
        
        form.addEventListener('submit', (e) => {
            const allAnswered = this.validateAllQuestions(questionCards, isMultipleChoice);
            
            if (!allAnswered) {
                e.preventDefault();
                this.showValidationError();
                this.scrollToFirstUnanswered(questionCards);
            }
        });

        this.setupRealTimeValidation(questionCards, isMultipleChoice);
    }

    isMultipleChoiceAssignment() {
        // Check if this is a multiple choice assignment
        const mcElements = document.querySelectorAll('input[type="radio"]');
        return mcElements.length > 0;
    }

    validateAllQuestions(questionCards, isMultipleChoice) {
        let allAnswered = true;
        
        questionCards.forEach((question, index) => {
            const answered = isMultipleChoice ? 
                this.isMultipleChoiceAnswered(question) : 
                this.isTextAnswerAnswered(question);
            
            this.updateQuestionStatus(question, answered);
            
            if (!answered) {
                allAnswered = false;
            }
        });
        
        return allAnswered;
    }

    isMultipleChoiceAnswered(question) {
        const radios = question.querySelectorAll('input[type="radio"]');
        return Array.from(radios).some(radio => radio.checked);
    }

    isTextAnswerAnswered(question) {
        const textarea = question.querySelector('textarea');
        return textarea && textarea.value.trim() !== '';
    }

    updateQuestionStatus(question, answered) {
        if (answered) {
            question.classList.add('answered');
            question.classList.remove('unanswered');
        } else {
            question.classList.add('unanswered');
            question.classList.remove('answered');
        }
    }

    setupRealTimeValidation(questionCards, isMultipleChoice) {
        if (isMultipleChoice) {
            this.setupRadioValidation(questionCards);
        } else {
            this.setTextareaValidation(questionCards);
        }
    }

    setupRadioValidation(questionCards) {
        questionCards.forEach(question => {
            const radios = question.querySelectorAll('input[type="radio"]');
            radios.forEach(radio => {
                radio.addEventListener('change', () => {
                    this.updateQuestionStatus(question, true);
                });
            });
        });
    }

    setTextareaValidation(questionCards) {
        questionCards.forEach(question => {
            const textarea = question.querySelector('textarea');
            if (textarea) {
                textarea.addEventListener('input', () => {
                    const answered = textarea.value.trim() !== '';
                    this.updateQuestionStatus(question, answered);
                    
                    if (answered) {
                        textarea.classList.remove('is-invalid');
                    }
                });
            }
        });
    }

    showValidationError() {
        // You could use a toast notification here
        alert('Please answer all questions before submitting.');
    }

    scrollToFirstUnanswered(questionCards) {
        const firstUnanswered = Array.from(questionCards).find(question => 
            question.classList.contains('unanswered')
        );
        
        if (firstUnanswered) {
            firstUnanswered.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    initAssignmentGrading() {
        // Grading functionality would go here
        this.setupGradingForm();
    }

    setupGradingForm() {
        const gradingForm = document.getElementById('gradingForm');
        if (gradingForm) {
            gradingForm.addEventListener('submit', (e) => {
                this.validateGradingForm(gradingForm);
            });
        }
    }

    validateGradingForm(form) {
        // Add grading form validation logic here
        console.log('Grading form validation');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    new AssignmentManager();
});