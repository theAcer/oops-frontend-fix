"use client";

import React, { useState, useEffect } from 'react';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Textarea } from '../ui/textarea';
import { LoyaltyProgramCreateRequest, LoyaltyProgramResponse, LoyaltyProgramUpdateRequest } from '../../types/api';
import { LoyaltyProgramType } from '../../types/enums';
import { Switch } from '../ui/switch';
import { Calendar } from '../ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover';
import { CalendarIcon } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '../../lib/utils';

interface LoyaltyProgramFormProps {
  initialData?: LoyaltyProgramResponse;
  onSubmit: (data: LoyaltyProgramCreateRequest | LoyaltyProgramUpdateRequest) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

const LoyaltyProgramForm = ({ initialData, onSubmit, onCancel, isSubmitting }: LoyaltyProgramFormProps) => {
  const [name, setName] = useState(initialData?.name || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [programType, setProgramType] = useState<LoyaltyProgramType>(initialData?.program_type as LoyaltyProgramType || LoyaltyProgramType.POINTS);
  const [pointsPerCurrency, setPointsPerCurrency] = useState(initialData?.points_per_currency?.toString() || '1.0');
  const [minimumSpend, setMinimumSpend] = useState(initialData?.minimum_spend?.toString() || '0.0');
  const [visitsRequired, setVisitsRequired] = useState(initialData?.visits_required?.toString() || '0');
  const [rewardVisits, setRewardVisits] = useState(initialData?.reward_visits?.toString() || '0');
  const [isActive, setIsActive] = useState(initialData?.is_active ?? true);
  const [startDate, setStartDate] = useState<Date | undefined>(initialData?.start_date ? new Date(initialData.start_date) : undefined);
  const [endDate, setEndDate] = useState<Date | undefined>(initialData?.end_date ? new Date(initialData.end_date) : undefined);

  useEffect(() => {
    if (initialData) {
      setName(initialData.name);
      setDescription(initialData.description || '');
      setProgramType(initialData.program_type as LoyaltyProgramType);
      setPointsPerCurrency(initialData.points_per_currency?.toString() || '1.0');
      setMinimumSpend(initialData.minimum_spend?.toString() || '0.0');
      setVisitsRequired(initialData.visits_required?.toString() || '0');
      setRewardVisits(initialData.reward_visits?.toString() || '0');
      setIsActive(initialData.is_active);
      setStartDate(initialData.start_date ? new Date(initialData.start_date) : undefined);
      setEndDate(initialData.end_date ? new Date(initialData.end_date) : undefined);
    }
  }, [initialData]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const data: LoyaltyProgramCreateRequest | LoyaltyProgramUpdateRequest = {
      name,
      description: description || undefined,
      program_type: programType,
      points_per_currency: parseFloat(pointsPerCurrency),
      minimum_spend: parseFloat(minimumSpend),
      visits_required: parseInt(visitsRequired),
      reward_visits: parseInt(rewardVisits),
      is_active: isActive,
      start_date: startDate ? startDate.toISOString() : undefined,
      end_date: endDate ? endDate.toISOString() : undefined,
    };

    onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit} className="grid gap-4 py-4">
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="name" className="text-right">
          Name
        </Label>
        <Input
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="col-span-3"
          required
        />
      </div>
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="description" className="text-right">
          Description
        </Label>
        <Textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="col-span-3"
        />
      </div>
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="programType" className="text-right">
          Program Type
        </Label>
        <Select value={programType} onValueChange={(value: LoyaltyProgramType) => setProgramType(value)}>
          <SelectTrigger id="programType" className="col-span-3">
            <SelectValue placeholder="Select program type" />
          </SelectTrigger>
          <SelectContent>
            {Object.values(LoyaltyProgramType).map((type) => (
              <SelectItem key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1).replace('_', ' ')}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {(programType === LoyaltyProgramType.POINTS || programType === LoyaltyProgramType.HYBRID || programType === LoyaltyProgramType.SPEND) && (
        <>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="pointsPerCurrency" className="text-right">
              Points per Ksh
            </Label>
            <Input
              id="pointsPerCurrency"
              type="number"
              step="0.1"
              value={pointsPerCurrency}
              onChange={(e) => setPointsPerCurrency(e.target.value)}
              className="col-span-3"
              required
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="minimumSpend" className="text-right">
              Minimum Spend (Ksh)
            </Label>
            <Input
              id="minimumSpend"
              type="number"
              step="0.01"
              value={minimumSpend}
              onChange={(e) => setMinimumSpend(e.target.value)}
              className="col-span-3"
              required
            />
          </div>
        </>
      )}

      {(programType === LoyaltyProgramType.VISITS || programType === LoyaltyProgramType.HYBRID) && (
        <>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="visitsRequired" className="text-right">
              Visits Required
            </Label>
            <Input
              id="visitsRequired"
              type="number"
              value={visitsRequired}
              onChange={(e) => setVisitsRequired(e.target.value)}
              className="col-span-3"
              required
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="rewardVisits" className="text-right">
              Reward Visits
            </Label>
            <Input
              id="rewardVisits"
              type="number"
              value={rewardVisits}
              onChange={(e) => setRewardVisits(e.target.value)}
              className="col-span-3"
              required
            />
          </div>
        </>
      )}

      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="startDate" className="text-right">
          Start Date
        </Label>
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant={"outline"}
              className={cn(
                "col-span-3 justify-start text-left font-normal",
                !startDate && "text-muted-foreground"
              )}
            >
              <CalendarIcon className="mr-2 h-4 w-4" />
              {startDate ? format(startDate, "PPP") : <span>Pick a date</span>}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0">
            <Calendar
              mode="single"
              selected={startDate}
              onSelect={setStartDate}
              initialFocus
            />
          </PopoverContent>
        </Popover>
      </div>

      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="endDate" className="text-right">
          End Date
        </Label>
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant={"outline"}
              className={cn(
                "col-span-3 justify-start text-left font-normal",
                !endDate && "text-muted-foreground"
              )}
            >
              <CalendarIcon className="mr-2 h-4 w-4" />
              {endDate ? format(endDate, "PPP") : <span>Pick a date</span>}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0">
            <Calendar
              mode="single"
              selected={endDate}
              onSelect={setEndDate}
              initialFocus
            />
          </PopoverContent>
        </Popover>
      </div>

      {initialData && ( // Only show active switch for existing programs
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="isActive" className="text-right">
            Active
          </Label>
          <Switch
            id="isActive"
            checked={isActive}
            onCheckedChange={setIsActive}
            className="col-span-3"
          />
        </div>
      )}

      <div className="flex justify-end gap-2 mt-4">
        <Button type="button" variant="outline" onClick={onCancel} disabled={isSubmitting}>
          Cancel
        </Button>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? (initialData ? 'Saving...' : 'Creating...') : (initialData ? 'Save Changes' : 'Create Program')}
        </Button>
      </div>
    </form>
  );
};

export default LoyaltyProgramForm;