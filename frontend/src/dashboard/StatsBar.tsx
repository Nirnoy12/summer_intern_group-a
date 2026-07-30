import { Card, CardHeader, CardTitle, CardContent } from "@/ui/card";
import { Trophy, Flame } from "lucide-react";
import { Progress } from "@/ui/progress";

export function StatsBar({ user }: { user: any }) {
  const xpForNextLevel = user.current_level * 500;
  const progressPercent = (user.total_xp / xpForNextLevel) * 100;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* Total XP */}
      <Card className="glass-card">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Total XP</CardTitle>
          <Trophy className="h-5 w-5 text-amber-500" />
        </CardHeader>
        <CardContent>
          <div className="text-4xl font-semibold tracking-tight">{user.total_xp}</div>
        </CardContent>
      </Card>

      {/* Current Level */}
      <Card className="glass-card">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Current Level</CardTitle>
          <div className="h-3 w-3 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
        </CardHeader>
        <CardContent>
          <div className="text-4xl font-semibold tracking-tight">Level {user.current_level}</div>
          <Progress value={progressPercent} className="h-2.5 mt-4 rounded-full bg-muted overflow-hidden [&>div]:bg-blue-500" />
          <p className="text-xs text-muted-foreground mt-3 font-medium">
            {xpForNextLevel - user.total_xp} XP to Level {user.current_level + 1}
          </p>
        </CardContent>
      </Card>

      {/* Learning Streak */}
      <Card className="glass-card">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Learning Streak</CardTitle>
          <Flame className="h-5 w-5 text-orange-500" />
        </CardHeader>
        <CardContent>
          <div className="text-4xl font-semibold tracking-tight">
            {user.current_streak} <span className="text-lg text-muted-foreground font-medium">Days</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
