package main

import (
	"fmt"
	"math"
	random "math/rand"
	"sort"
)

type PropertyAllocator struct {
	ratio            map[string]int
	dbCount          map[string]int
	limit            int
	propertyCountMap map[string]int
	priorityList     []string
	result           []string
}

func NewPropertyAllocator(ratio map[string]int, dbCount map[string]int, limit int) *PropertyAllocator {
	return &PropertyAllocator{
		ratio:            ratio,
		dbCount:          dbCount,
		limit:            limit,
		propertyCountMap: make(map[string]int),
		priorityList:     []string{},
		result:           []string{},
	}
}

func (pa *PropertyAllocator) makePropertyCountMap() {
	for partner, partnerRatio := range pa.ratio {
		pa.propertyCountMap[partner] = int(math.Ceil(float64(partnerRatio) * float64(pa.limit) * 0.01))
	}
}

func (pa *PropertyAllocator) makePriorityList() {
	type partnerCount struct {
		partner string
		count   int
	}

	pairs := make([]partnerCount, 0, len(pa.propertyCountMap))
	for partner, count := range pa.propertyCountMap {
		pairs = append(pairs, partnerCount{partner, count})
	}

	sort.Slice(pairs, func(i, j int) bool {
		if pairs[i].count != pairs[j].count {
			return pairs[i].count > pairs[j].count
		}
		return pairs[i].partner < pairs[j].partner
	})

	for _, p := range pairs {
		pa.priorityList = append(pa.priorityList, p.partner)
	}
}

func (pa *PropertyAllocator) reduceOneFromHighestPriority(totalProperty int) int {
	for _, partner := range pa.priorityList {
		if pa.propertyCountMap[partner] > 1 {
			pa.propertyCountMap[partner]--
			return totalProperty - 1
		}
	}
	return totalProperty
}

func (pa *PropertyAllocator) reduceFromLowestPriorities(totalProperty int, minCount int) int {
	for i := len(pa.priorityList) - 1; i >= 0; i-- {
		if totalProperty <= pa.limit {
			break
		}
		partner := pa.priorityList[i]
		if pa.propertyCountMap[partner] > minCount {
			pa.propertyCountMap[partner]--
			totalProperty--
		}
	}
	return totalProperty
}

func (pa *PropertyAllocator) reduceExtraProperties() {
	totalProperty := 0
	for _, count := range pa.propertyCountMap {
		totalProperty += count
	}

	if totalProperty <= pa.limit {
		return
	}

	// 1. Reduce one from the highest-priority partner that has > 1
	totalProperty = pa.reduceOneFromHighestPriority(totalProperty)

	// 2. Reduce from lowest to highest priority (partners with > 1) until limit met.
	totalProperty = pa.reduceFromLowestPriorities(totalProperty, 1)

	// 3. Fallback: allow reducing to 0 if still over limit
	if totalProperty > pa.limit {
		pa.reduceFromLowestPriorities(totalProperty, 0)
	}
}

func (pa *PropertyAllocator) adjustForDatabaseLimit() int {
	remainingCount := 0

	for partner, availableCount := range pa.dbCount {
		assignedCount := pa.propertyCountMap[partner]

		if availableCount < assignedCount {
			extraCount := assignedCount - availableCount
			remainingCount += extraCount
			pa.propertyCountMap[partner] = availableCount
		}
	}

	return remainingCount
}

func (pa *PropertyAllocator) redistributeRemainingProperties(remainingCount int) {
	totalAvailable := 0
	for _, count := range pa.dbCount {
		totalAvailable += count
	}

	currentTotal := 0
	for _, count := range pa.propertyCountMap {
		currentTotal += count
	}

	for remainingCount > 0 && currentTotal < totalAvailable {
		addedProperty := false

		for _, partner := range pa.priorityList {
			if pa.propertyCountMap[partner] >= pa.dbCount[partner] {
				continue
			}

			pa.propertyCountMap[partner]++
			currentTotal++
			remainingCount--
			addedProperty = true

			if remainingCount == 0 {
				return
			}
		}

		if !addedProperty {
			return
		}
	}
}

func (pa *PropertyAllocator) buildResult() {
	for partner, propertyCount := range pa.propertyCountMap {
		for i := 0; i < propertyCount; i++ {
			pa.result = append(pa.result, partner)
		}
	}

	random.Shuffle(len(pa.result), func(i, j int) {
		pa.result[i], pa.result[j] = pa.result[j], pa.result[i]
	})
}

func (pa *PropertyAllocator) ShowProperty() []string {
	pa.makePropertyCountMap()
	pa.makePriorityList()
	pa.reduceExtraProperties()
	remainingCount := pa.adjustForDatabaseLimit()
	pa.redistributeRemainingProperties(remainingCount)
	pa.buildResult()
	return pa.result
}

func main() {
	limit := 192
	ratio := map[string]int{"11": 1, "12": 98, "24": 1}
	dbCount := map[string]int{"11": 0, "12": 80, "24": 50}

	allocator := NewPropertyAllocator(ratio, dbCount, limit)
	output := allocator.ShowProperty()
	fmt.Println(output)
}
