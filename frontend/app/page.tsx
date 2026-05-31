"use client";

import { useState } from "react";

type ItineraryItem = {
  time: string;
  title: string;
  location: string;
  type: string;
  duration_min: number;
  estimated_cost: number;
  walking_minutes: number;
  risk_score: number;
  utility_score: number;
  reason: string;
  can_skip: boolean;
};

type MatchdayResponse = {
  itinerary_id: string;
  city: string;
  stadium: string;
  arrival_risk: string;
  time_slack_minutes: number;
  total_estimated_cost: number;
  total_walking_minutes: number;
  itinerary: ItineraryItem[];
  agent_explanation: string;
};

const API_BASE_URL = "http://127.0.0.1:8000";

export default function Home() {
  const [plan, setPlan] = useState<MatchdayResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function createPlan() {
    setLoading(true);

    const response = await fetch(`${API_BASE_URL}/plan-matchday`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        start_location: "Downtown Seattle",
        kickoff_time: "6:00 PM",
        food_preference: "vegetarian",
        budget: "medium",
        walking_tolerance: "moderate",
        travel_style: "balanced",
        arrival_buffer_minutes: 90,
      }),
    });

    const data = await response.json();
    setPlan(data);
    setLoading(false);
  }

  async function replan(trigger: string) {
    if (!plan) return;

    setLoading(true);

    const response = await fetch(`${API_BASE_URL}/replan-matchday`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        itinerary_id: plan.itinerary_id,
        trigger,
      }),
    });

    const data = await response.json();
    setPlan(data);
    setLoading(false);
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="mx-auto flex max-w-7xl flex-col gap-10 px-6 py-10 lg:px-8">
        <nav className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-emerald-400">
              MatchDay by Swanavi
            </p>
            <h1 className="text-2xl font-bold tracking-tight">
              World Cup 2026 AI Matchday Agent
            </h1>
          </div>
          <div className="rounded-full border border-white/10 px-4 py-2 text-sm text-slate-300">
            Seattle → Lumen Field
          </div>
        </nav>

        <section className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div className="space-y-6">
            <div className="inline-flex rounded-full border border-emerald-400/30 bg-emerald-400/10 px-4 py-2 text-sm text-emerald-300">
              Powered by agentic planning, dynamic replanning, and itinerary risk scoring
            </div>

            <h2 className="max-w-4xl text-5xl font-bold tracking-tight sm:text-6xl">
              Plan your perfect World Cup matchday, then adapt when real life happens.
            </h2>

            <p className="max-w-2xl text-lg leading-8 text-slate-300">
              MatchDay creates a personalized Seattle matchday itinerary around food,
              budget, walking tolerance, kickoff time, and stadium arrival risk. If
              you are late, tired, over budget, or want less walking, the agent replans
              the day while protecting your arrival buffer.
            </p>

            <div className="flex flex-wrap gap-3">
              <button
                onClick={createPlan}
                disabled={loading}
                className="rounded-2xl bg-emerald-400 px-6 py-3 font-semibold text-slate-950 shadow-lg shadow-emerald-400/20 transition hover:bg-emerald-300 disabled:opacity-60"
              >
                {loading ? "Planning..." : "Plan My Matchday"}
              </button>

              <a
                href="#demo"
                className="rounded-2xl border border-white/10 px-6 py-3 font-semibold text-slate-200 transition hover:bg-white/10"
              >
                View Demo Flow
              </a>
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl">
            <div className="rounded-2xl bg-slate-900 p-5">
              <p className="text-sm text-slate-400">Demo profile</p>
              <div className="mt-4 grid gap-3">
                <InfoRow label="Start" value="Downtown Seattle" />
                <InfoRow label="Kickoff" value="6:00 PM" />
                <InfoRow label="Food" value="Vegetarian" />
                <InfoRow label="Budget" value="Medium" />
                <InfoRow label="Walking" value="Moderate" />
                <InfoRow label="Buffer" value="90 minutes" />
              </div>
            </div>
          </div>
        </section>

        {plan && (
          <section id="demo" className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
            <aside className="space-y-6">
              <div className="rounded-3xl border border-white/10 bg-white/5 p-6">
                <h3 className="text-xl font-bold">Agent Risk Dashboard</h3>
                <div className="mt-5 grid gap-3">
                  <Metric label="City" value={plan.city} />
                  <Metric label="Stadium" value={plan.stadium} />
                  <Metric label="Arrival Risk" value={plan.arrival_risk} />
                  <Metric
                    label="Time Slack"
                    value={`${plan.time_slack_minutes} min`}
                  />
                  <Metric
                    label="Estimated Cost"
                    value={`$${plan.total_estimated_cost}`}
                  />
                  <Metric
                    label="Walking"
                    value={`${plan.total_walking_minutes} min`}
                  />
                </div>
              </div>

              <div className="rounded-3xl border border-white/10 bg-white/5 p-6">
                <h3 className="text-xl font-bold">Replan Actions</h3>
                <p className="mt-2 text-sm text-slate-400">
                  Trigger realistic matchday disruptions and watch the agent update
                  the itinerary.
                </p>

                <div className="mt-5 grid gap-3">
                  <ReplanButton
                    label="I’m 30 min late"
                    onClick={() => replan("late_30")}
                  />
                  <ReplanButton
                    label="Find cheaper food"
                    onClick={() => replan("cheaper_food")}
                  />
                  <ReplanButton
                    label="Less walking"
                    onClick={() => replan("less_walking")}
                  />
                  <ReplanButton
                    label="Go straight to stadium"
                    onClick={() => replan("go_straight_to_stadium")}
                  />
                </div>
              </div>

              <div className="rounded-3xl border border-emerald-400/20 bg-emerald-400/10 p-6">
                <h3 className="text-xl font-bold text-emerald-300">
                  Agent Explanation
                </h3>
                <p className="mt-3 leading-7 text-slate-200">
                  {plan.agent_explanation}
                </p>
              </div>
            </aside>

            <section className="rounded-3xl border border-white/10 bg-white/5 p-6">
              <h3 className="text-2xl font-bold">Matchday Timeline</h3>
              <p className="mt-2 text-slate-400">
                A live itinerary optimized around kickoff, budget, walking, and
                arrival risk.
              </p>

              <div className="mt-8 space-y-5">
                {plan.itinerary.map((item, index) => (
                  <div key={`${item.time}-${item.title}`} className="relative">
                    {index !== plan.itinerary.length - 1 && (
                      <div className="absolute left-[18px] top-10 h-full w-px bg-white/10" />
                    )}

                    <div className="flex gap-4">
                      <div className="relative z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-emerald-400 text-sm font-bold text-slate-950">
                        {index + 1}
                      </div>

                      <div className="w-full rounded-2xl border border-white/10 bg-slate-900 p-5">
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div>
                            <p className="text-sm font-semibold text-emerald-300">
                              {item.time}
                            </p>
                            <h4 className="mt-1 text-lg font-bold">
                              {item.title}
                            </h4>
                            <p className="text-sm text-slate-400">
                              {item.location}
                            </p>
                          </div>

                          <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-slate-300">
                            {item.type}
                          </span>
                        </div>

                        <div className="mt-4 grid gap-2 text-sm text-slate-300 sm:grid-cols-4">
                          <SmallMetric label="Cost" value={`$${item.estimated_cost}`} />
                          <SmallMetric
                            label="Walk"
                            value={`${item.walking_minutes}m`}
                          />
                          <SmallMetric
                            label="Risk"
                            value={item.risk_score.toFixed(2)}
                          />
                          <SmallMetric
                            label="Utility"
                            value={item.utility_score.toFixed(2)}
                          />
                        </div>

                        <p className="mt-4 text-sm leading-6 text-slate-300">
                          {item.reason}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </section>
        )}
      </section>
    </main>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-xl bg-white/5 px-4 py-3">
      <span className="text-sm text-slate-400">{label}</span>
      <span className="font-medium text-slate-100">{value}</span>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-center justify-between rounded-xl bg-slate-900 px-4 py-3">
      <span className="text-sm text-slate-400">{label}</span>
      <span className="font-semibold text-white">{value}</span>
    </div>
  );
}

function SmallMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-white/5 px-3 py-2">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="font-semibold text-slate-100">{value}</p>
    </div>
  );
}

function ReplanButton({
  label,
  onClick,
}: {
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="rounded-2xl border border-white/10 bg-slate-900 px-4 py-3 text-left font-medium text-slate-100 transition hover:border-emerald-400/40 hover:bg-emerald-400/10"
    >
      {label}
    </button>
  );
}