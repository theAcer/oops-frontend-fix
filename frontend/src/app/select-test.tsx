import React, { useState } from 'react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'

export function WorkingSelectTest() {
  const [value, setValue] = useState('')

  const handleValueChange = (newValue: string) => {
    console.log('Value changed to:', newValue)
    setValue(newValue)
  }

  return (
    <div className="p-8 max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-6">Select Component Test</h1>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Test Select:</label>
          <Select value={value} onValueChange={handleValueChange}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Choose an option" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="retail">Retail Store</SelectItem>
              <SelectItem value="restaurant">Restaurant</SelectItem>
              <SelectItem value="service">Service Business</SelectItem>
              <SelectItem value="salon">Beauty Salon</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="p-4 bg-gray-100 rounded">
          <p className="text-sm">
            <strong>Selected Value:</strong> {value || 'None'}
          </p>
          <p className="text-sm mt-2">
            <strong>Debug Info:</strong> This should show the selected value above
          </p>
        </div>
      </div>
    </div>
  )
}
