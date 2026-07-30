import { CheckCircle2, XCircle } from "lucide-react";
import { Button } from "@/ui/button";

interface QuizResultProps {
  result: any;
  loadQuiz: () => void;
  onSkip?: () => void;
}

export function QuizResult({ result, loadQuiz, onSkip }: QuizResultProps) {
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
      <div className="flex gap-3">
        {!result.passed && (
          <Button size="lg" onClick={loadQuiz}>
            Retake Quiz
          </Button>
        )}
        {onSkip && (
          <Button size="lg" variant="outline" onClick={onSkip}>
            Continue to Next Video
          </Button>
        )}
      </div>
    </div>
  );
}
