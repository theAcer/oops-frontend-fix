"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../lib/api';
import { LoyaltyProgramResponse, LoyaltyProgramCreateRequest, LoyaltyProgramUpdateRequest, LoyaltyAnalytics } from '../../types/api';
import { toast } from 'react-hot-toast';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { PlusCircle, Terminal, Users, DollarSign, Gift } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../../components/ui/dialog';
import { Alert, AlertDescription, AlertTitle } from '../../components/ui/alert';
import LoyaltyProgramCard from '../../components/loyalty/LoyaltyProgramCard';
import LoyaltyProgramForm from '../../components/loyalty/LoyaltyProgramForm';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Separator } from '../../components/ui/separator';

const LoyaltyPage = () => {
  const { user, loading: authLoading } = useAuth();
  const [programs, setPrograms] = useState<LoyaltyProgramResponse[]>([]);
  const [analytics, setAnalytics] = useState<LoyaltyAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isFormDialogOpen, setIsFormDialogOpen] = useState(false);
  const [editingProgram, setEditingProgram] = useState<LoyaltyProgramResponse | undefined>(undefined);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchLoyaltyData = async () => {
    if (!user?.merchant_id) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const programsResponse = await api.get<LoyaltyProgramResponse[]>(`/api/v1/loyalty/programs?merchant_id=${user.merchant_id}`);
      setPrograms(programsResponse.data);

      const analyticsResponse = await api.get<LoyaltyAnalytics>(`/api/v1/loyalty/analytics/${user.merchant_id}`);
      setAnalytics(analyticsResponse.data);

    } catch (err: any) {
      console.error('Failed to fetch loyalty data:', err);
      setError(err.response?.data?.detail || 'Failed to load loyalty data.');
      toast.error(err.response?.data?.detail || 'Failed to load loyalty data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading && user?.merchant_id) {
      fetchLoyaltyData();
    }
  }, [authLoading, user?.merchant_id]);

  const handleCreateOrUpdateProgram = async (data: LoyaltyProgramCreateRequest | LoyaltyProgramUpdateRequest) => {
    setIsSubmitting(true);
    try {
      if (editingProgram) {
        // Update existing program
        await api.put<LoyaltyProgramResponse>(`/api/v1/loyalty/programs/${editingProgram.id}`, data);
        toast.success('Loyalty program updated successfully!');
      } else {
        // Create new program
        const createData: LoyaltyProgramCreateRequest = { ...data, merchant_id: user!.merchant_id! } as LoyaltyProgramCreateRequest;
        await api.post<LoyaltyProgramResponse>('/api/v1/loyalty/programs', createData);
        toast.success('Loyalty program created successfully!');
      }
      setIsFormDialogOpen(false);
      setEditingProgram(undefined);
      fetchLoyaltyData(); // Refresh data
    } catch (err: any) {
      console.error('Failed to save loyalty program:', err);
      toast.error(err.response?.data?.detail || 'Failed to save loyalty program. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEditProgram = (program: LoyaltyProgramResponse) => {
    setEditingProgram(program);
    setIsFormDialogOpen(true);
  };

  const handleActivateProgram = async (programId: number) => {
    try {
      await api.post(`/api/v1/loyalty/programs/${programId}/activate`);
      toast.success('Loyalty program activated successfully!');
      fetchLoyaltyData(); // Refresh data
    } catch (err: any) {
      console.error('Failed to activate loyalty program:', err);
      toast.error(err.response?.data?.detail || 'Failed to activate loyalty program. Please try again.');
    }
  };

  if (authLoading || loading) {
    return <div className="text-center py-8">Loading loyalty data...</div>;
  }

  if (error) {
    return (
      <div className="p-4">
        <Alert variant="destructive">
          <Terminal className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (!user?.merchant_id) {
    return (
      <div className="p-4">
        <Alert>
          <Terminal className="h-4 w-4" />
          <AlertTitle>No Merchant Linked!</AlertTitle>
          <AlertDescription>
            Please link a business to manage loyalty programs.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Loyalty Programs</h1>

      <Tabs defaultValue="programs" className="space-y-4">
        <TabsList>
          <TabsTrigger value="programs">Programs</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="programs" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold">Your Programs</h2>
            <Button onClick={() => { setEditingProgram(undefined); setIsFormDialogOpen(true); }}>
              <PlusCircle className="mr-2 h-4 w-4" /> Create New Program
            </Button>
          </div>

          {programs.length === 0 ? (
            <Alert>
              <Terminal className="h-4 w-4" />
              <AlertTitle>No Loyalty Programs Found</AlertTitle>
              <AlertDescription>
                You haven't created any loyalty programs yet. Click "Create New Program" to get started!
              </AlertDescription>
            </Alert>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {programs.map((program) => (
                <LoyaltyProgramCard
                  key={program.id}
                  program={program}
                  onEdit={handleEditProgram}
                  onActivate={handleActivateProgram}
                />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <h2 className="text-2xl font-semibold">Loyalty Analytics</h2>
          {analytics ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Members</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics.total_members.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">
                    Customers enrolled in loyalty program
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Average Points</CardTitle>
                  <Gift className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics.average_points.toFixed(0)}</div>
                  <p className="text-xs text-muted-foreground">
                    Average points per active member
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Points Issued</CardTitle>
                  <Gift className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics.total_points_issued.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">
                    Lifetime points awarded
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Reward Redemption Rate</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics.rewards.redemption_rate.toFixed(2)}%</div>
                  <p className="text-xs text-muted-foreground">
                    Of all issued rewards
                  </p>
                </CardContent>
              </Card>

              <Card className="col-span-full">
                <CardHeader>
                  <CardTitle>Tier Distribution</CardTitle>
                  <CardDescription>Breakdown of customers by loyalty tier.</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(analytics.tier_distribution).map(([tier, count]) => (
                      <div key={tier} className="flex flex-col items-center justify-center p-4 border rounded-md">
                        <p className="text-lg font-semibold capitalize">{tier}</p>
                        <p className="text-3xl font-bold">{count}</p>
                        <p className="text-sm text-muted-foreground">Members</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <Alert>
              <Terminal className="h-4 w-4" />
              <AlertTitle>No Analytics Available</AlertTitle>
              <AlertDescription>
                No loyalty analytics available yet. Create a program and start earning!
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>
      </Tabs>

      {/* Loyalty Program Form Dialog */}
      <Dialog open={isFormDialogOpen} onOpenChange={setIsFormDialogOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>{editingProgram ? 'Edit Loyalty Program' : 'Create New Loyalty Program'}</DialogTitle>
            <DialogDescription>
              {editingProgram ? 'Make changes to your loyalty program here.' : 'Set up a new loyalty program for your customers.'}
            </DialogDescription>
          </DialogHeader>
          <LoyaltyProgramForm
            initialData={editingProgram}
            onSubmit={handleCreateOrUpdateProgram}
            onCancel={() => { setIsFormDialogOpen(false); setEditingProgram(undefined); }}
            isSubmitting={isSubmitting}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default LoyaltyPage;