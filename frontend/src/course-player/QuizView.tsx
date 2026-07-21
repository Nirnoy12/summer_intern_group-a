import { useState, useEffect } from "react";
import { Button } from "@/ui/button";
import { Card } from "@/ui/card";
import { Loader2, CheckCircle2, XCircle } from "lucide-react";
import API from "@/auth/auth";
import { useAuth } from "@/auth/AuthContext";

export function QuizView({ quiz, onPassed }: { quiz: any; onPassed: () => void }) {
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [questions, setQuestions] = useState<any[]>([]);
  const [attemptId, setAttemptId] = useState<string | null>(null);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);

  const loadQuiz = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await API.get(`/api/quizzes/${quiz.id}/start`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.data.status === "ready") {
        setQuestions(res.data.questions);
        setAttemptId(res.data.attempt_id);
        setAnswers({});
        setResult(null);
      } else {
        setError(res.data.message || "Quiz is still generating...");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to start quiz.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQuiz();
  }, [quiz.id, token]);

  const handleSelect = (qId: string, index: number) => {
    setAnswers((prev) => ({ ...prev, [qId]: index }));
  };

  const handleSubmit = async () => {
    if (!attemptId) return;
    setSubmitting(true);
    try {
      const res = await API.post(
        `/api/quizzes/${quiz.id}/submit`,
        {
          attempt_id: attemptId,
          answers,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setResult(res.data);
      if (res.data.passed) {
        onPassed();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to submit quiz.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-muted-foreground gap-4">
        <Loader2 className="h-8 w-8 animate-spin" />
        <p>Loading Quiz...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center gap-4">
        <p className="text-red-500">{error}</p>
        <Button onClick={loadQuiz}>Retry</Button>
      </div>
    );
  }

  if (result) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center gap-6 animate-in fade-in zoom-in duration-300">
        {result.passed ? (
          <CheckCircle2 className="h-20 w-20 text-green-500" />
        ) : (
          <XCircle className="h-20 w-20 text-destructive" />
        )}
        <h2 className="text-3xl font-bold">
          {result.passed ? "Quiz Passed!" : "Quiz Failed"}
        </h2>
        <p className="text-xl">
          Score: <span className="font-bold">{result.score}%</span>
        </p>
        <p className="text-muted-foreground">
          You got {result.correct_count} out of {result.total} questions correct.
        </p>
        {!result.passed && (
          <Button size="lg" onClick={loadQuiz}>
            Retake Quiz (Different Questions)
          </Button>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-hidden bg-background">
      <div className="p-4 border-b">
        <h2 className="text-xl font-bold">{quiz.title}</h2>
        <p className="text-sm text-muted-foreground">Answer all questions to continue.</p>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-8">
        {questions.map((q, idx) => (
          <Card key={q.id} className="p-6 space-y-4 shadow-sm border-border">
            <h3 className="font-medium text-lg leading-relaxed">
              <span className="text-primary font-bold mr-2">{idx + 1}.</span>
              {q.question_text}
            </h3>
            <div className="space-y-2">
              {q.options.map((opt: string, optIdx: number) => (
                <button
                  key={optIdx}
                  onClick={() => handleSelect(q.id, optIdx)}
                  className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${
                    answers[q.id] === optIdx
                      ? "border-primary bg-primary/10 ring-1 ring-primary shadow-sm"
                      : "border-border hover:border-primary/50 hover:bg-accent/50"
                  }`}
                >
                  {opt}
                </button>
              ))}
            </div>
          </Card>
        ))}
      </div>

      <div className="p-4 border-t bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <Button 
          className="w-full shadow-lg" 
          size="lg" 
          onClick={handleSubmit} 
          disabled={submitting || Object.keys(answers).length < questions.length}
        >
          {submitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
          Submit Quiz
        </Button>
        {Object.keys(answers).length < questions.length && (
          <p className="text-xs text-center text-muted-foreground mt-2">
            Please answer all questions before submitting.
          </p>
        )}
      </div>
    </div>
  );
}
