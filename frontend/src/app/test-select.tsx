import React, { useState } from 'react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'

export function TestSelect() {
  const [value, setValue] = useState('')

  return (
    <div className="p-4">
      <h2 className="text-lg font-bold mb-4">Select Component Test</h2>
      <Select value={value} onValueChange={setValue}>
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Select an option" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="option1">Option 1</SelectItem>
          <SelectItem value="option2">Option 2</SelectItem>
          <SelectItem value="option3">Option 3</SelectItem>
        </SelectContent>
      </Select>
      <p className="mt-2 text-sm text-gray-600">Selected value: {value}</p>
    </div>
  )
}
