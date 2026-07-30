import { Card } from "@/ui/card";

interface QuizQuestionProps {
  question: any;
  index: number;
  answerIndex?: number;
  onSelect: (index: number) => void;
}

export function QuizQuestion({ question, index, answerIndex, onSelect }: QuizQuestionProps) {
  return (
    <Card className="p-6 space-y-4 shadow-sm border-border">
      <h3 className="font-medium text-lg leading-relaxed">
        <span className="text-primary font-bold mr-2">{index + 1}.</span>
        {question.question_text}
      </h3>
      <div className="space-y-2">
        {question.options.map((opt: string, optIdx: number) => (
          <button
            key={optIdx}
            onClick={() => onSelect(optIdx)}
            className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${
              answerIndex === optIdx
                ? "border-primary bg-primary/10 ring-1 ring-primary shadow-sm"
                : "border-border hover:border-primary/50 hover:bg-accent/50"
            }`}
          >
            {opt}
          </button>
        ))}
      </div>
    </Card>
  );
}
