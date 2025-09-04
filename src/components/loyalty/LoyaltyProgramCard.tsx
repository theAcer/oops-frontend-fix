"use client";

import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { LoyaltyProgramResponse } from '../../types/api';
import { format } from 'date-fns';
import { CheckCircle2, XCircle, Edit, PlayCircle } from 'lucide-react';

interface LoyaltyProgramCardProps {
  program: LoyaltyProgramResponse;
  onEdit: (program: LoyaltyProgramResponse) => void;
  onActivate: (programId: number) => void;
}

const LoyaltyProgramCard = ({ program, onEdit, onActivate }: LoyaltyProgramCardProps) => {
  const isActive = program.is_active;

  const getProgramTypeLabel = (type: string) => {
    switch (type) {
      case 'points': return 'Points-Based';
      case 'visits': return 'Visits-Based';
      case 'spend': return 'Spend-Based';
      case 'hybrid': return 'Hybrid';
      default: return type;
    }
  };

  return (
    <Card className="flex flex-col h-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{program.name}</CardTitle>
          <Badge variant={isActive ? 'default' : 'secondary'}>
            {isActive ? 'Active' : 'Inactive'}
          </Badge>
        </div>
        <CardDescription>{program.description || 'No description provided.'}</CardDescription>
      </CardHeader>
      <CardContent className="flex-grow space-y-2 text-sm">
        <p className="flex items-center">
          <span className="font-medium w-32">Type:</span>
          <span className="ml-2">{getProgramTypeLabel(program.program_type)}</span>
        </p>
        {program.program_type === 'points' || program.program_type === 'hybrid' ? (
          <>
            <p className="flex items-center">
              <span className="font-medium w-32">Points per Ksh:</span>
              <span className="ml-2">{program.points_per_currency}</span>
            </p>
            <p className="flex items-center">
              <span className="font-medium w-32">Min. Spend:</span>
              <span className="ml-2">Ksh {program.minimum_spend.toLocaleString()}</span>
            </p>
          </>
        ) : null}
        {program.program_type === 'visits' || program.program_type === 'hybrid' ? (
          <>
            <p className="flex items-center">
              <span className="font-medium w-32">Visits Required:</span>
              <span className="ml-2">{program.visits_required}</span>
            </p>
            <p className="flex items-center">
              <span className="font-medium w-32">Reward Visits:</span>
              <span className="ml-2">{program.reward_visits}</span>
            </p>
          </>
        ) : null}
        <p className="flex items-center">
          <span className="font-medium w-32">Created:</span>
          <span className="ml-2">{format(new Date(program.created_at), 'PPP')}</span>
        </p>
        {program.start_date && (
          <p className="flex items-center">
            <span className="font-medium w-32">Starts:</span>
            <span className="ml-2">{format(new Date(program.start_date), 'PPP')}</span>
          </p>
        )}
        {program.end_date && (
          <p className="flex items-center">
            <span className="font-medium w-32">Ends:</span>
            <span className="ml-2">{format(new Date(program.end_date), 'PPP')}</span>
          </p>
        )}
      </CardContent>
      <CardFooter className="flex justify-end gap-2 pt-4">
        {!isActive && (
          <Button variant="outline" size="sm" onClick={() => onActivate(program.id)}>
            <PlayCircle className="mr-2 h-4 w-4" /> Activate
          </Button>
        )}
        <Button variant="secondary" size="sm" onClick={() => onEdit(program)}>
          <Edit className="mr-2 h-4 w-4" /> Edit
        </Button>
      </CardFooter>
    </Card>
  );
};

export default LoyaltyProgramCard;