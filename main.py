import math, random


class PropertyAllocator:
    def __init__(self, ratio: dict[str, int], db_count: dict[str, int], limit: int):
        self.ratio = ratio
        self.db_count = db_count
        self.limit = limit
        self.property_count_map = {}
        self.priority_list = []
        self.result = []

    def _make_property_count_map(self) -> None:
        for partner, partner_ratio in self.ratio.items():
            self.property_count_map[partner] = math.ceil(partner_ratio * self.limit * 0.01)

    def _make_priority_list(self) -> None:
        for partner, _ in sorted(self.property_count_map.items(),key=lambda item: (-item[1], item[0])):
            self.priority_list.append(partner)

    def _reduce_one_from_highest_priority(self, total_property: int) -> int:
        for partner in self.priority_list:
            if self.property_count_map[partner] > 1:
                self.property_count_map[partner] -= 1
                return total_property - 1
        return total_property

    def _reduce_from_lowest_priorities(self, total_property: int, min_count: int) -> int:
        for partner in reversed(self.priority_list):
            if total_property <= self.limit:
                break
            if self.property_count_map[partner] > min_count:
                self.property_count_map[partner] -= 1
                total_property -= 1
        return total_property

    def _reduce_extra_properties(self) -> None:
        total_property = sum(self.property_count_map.values())

        if total_property <= self.limit:
            return

        # 1. Reduce one from the highest-priority partner that has > 1
        total_property = self._reduce_one_from_highest_priority(total_property)

        # 2. Reduce from lowest to highest priority (partners with > 1) until limit met.
        total_property = self._reduce_from_lowest_priorities(total_property, min_count=1)

        # 3. Fallback: allow reducing to 0 if still over limit
        if total_property > self.limit:
            self._reduce_from_lowest_priorities(total_property, min_count=0)

    def _adjust_for_database_limit(self) -> int:
        remaining_count: int = 0

        for partner, available_count in self.db_count.items():
            assigned_count: int = self.property_count_map.get(partner, 0)

            if available_count < assigned_count:
                extra_count = assigned_count - available_count
                remaining_count += extra_count
                self.property_count_map[partner] = available_count

        return remaining_count

    def _redistribute_remaining_properties(self, remaining_count: int) -> None:
        total_available: int = sum(self.db_count.values())
        current_total: int = sum(self.property_count_map.values())

        while remaining_count and  current_total < total_available:
            added_property: bool = False

            for partner in self.priority_list:
                if self.property_count_map[partner] >= self.db_count[partner]:
                    continue

                self.property_count_map[partner] += 1
                current_total += 1
                remaining_count -= 1
                added_property = True

                if not remaining_count:
                    return

            if not added_property:
                return

    def _build_result(self) -> None:
        for partner, property_count in self.property_count_map.items():
            self.result.extend([partner] * property_count)
        
        random.shuffle(self.result)

    def show_property(self) -> list[str]:
        self._make_property_count_map()
        self._make_priority_list()
        self._reduce_extra_properties()
        remaining_count: int = self._adjust_for_database_limit()
        self._redistribute_remaining_properties(remaining_count)
        self._build_result()
        return self.result


if __name__ == "__main__":
    limit: int = 192
    ratio: dict[str, int] = {"11": 1, "12": 98, "24": 1}
    db_count: dict[str, int] = {"11": 0, "12": 80, "24": 50}

    allocator = PropertyAllocator(ratio, db_count, limit)
    output: list[str] = allocator.show_property()
    print(output)