import copy

from implementation.circle import *
import implementation.event_handling as eh
import implementation.algo_utils as au

class Push_down_algo_adj:
    """
    Variation of algo used for Caida-experiment.
    Here, we stop the algo once the traditional variant fails, and we return the circle
    """
    def __init__(self, circle, check_failure):
        self.circle = circle
        self.debug = False
        self.random_adjustment = False

        self.access_cost = 0
        self.reconfig_cost = 0
        self.deleted_items = 0
        self.inserts_after_init = 0
        self.reinserted_items = 0

        self.sum_del_items = 0
        self.sum_reinserted_items = 0
        self.max_iteration = 0

        self.check_failure = check_failure

    def serve_sequence(self, sequence, type, max_served_events=None):
        """
        Serve the sequence of requests passed as parameter.
        The parameter is used to create an event queue, on which the algo will work
        Distinguishes a deleting from an access event
        """
        self.circle.checking_failure = self.check_failure
        queue = eh.create_queue(sequence=sequence, circle=self.circle, type=type)
        event_seq = copy.deepcopy(queue)  # deep copy = events are also duplicated (not just ref)
        print(f"Event queue counts {len(event_seq)} events, now serving maximum of {max_served_events} events")
        print(f"Starting to work through event queue, circle-checking_failure={self.circle.checking_failure}")
        accessed_items = 0
        if self.debug:
            with open("serv_cap_test.txt", "at") as f:
                f.write(f"Algo: Server capacity capped at {self.circle.server_capacity}\n\n")
        if not max_served_events:
            breaking_real_event = 9999999999     # just a number that won't be reached
        elif type == "ctr":
            constraint_event_id = {25000: 79327, 50000: 50079, 75000: 24932}
            breaking_real_event = constraint_event_id[max_served_events]
        num_acc_constraint = max_served_events
        while not event_seq.is_empty():
            curr_event = event_seq.delete()     # pop queue, event after event
            if type == "ctr":
                if curr_event.id == breaking_real_event:
                    print(f"Stopping at event {curr_event.id} cause we reached constraint, after {accessed_items} accesses!")
                    break
            elif type == "temp":
                if max_served_events:
                    if not num_acc_constraint:
                        print(f"Stopping at event {curr_event.id} cause of access constraint: {num_acc_constraint}!")
                        break
            if curr_event.get_type() == "access":       # access event
                accessed_items += 1
                if max_served_events:
                    num_acc_constraint -= 1
                self.check_insertion_need(curr_event)  # insert item if needed
                if self.check_failure:
                    if self.circle.traditional_algo_failed:      # if no_failure == False -> failure, stop!
                        print(f"!!! Traditional failed at {self.circle.failed_at}, returning circle !!!")
                        return self.circle

                # if item not found in given server, search for item and create an AccessEvent on the correct server
                if not au.lookup(circle=self.circle, debug=self.debug,
                                 item_id=curr_event.item_id, server_id=curr_event.inserting_server):
                    au.search_update_queue(circle=self.circle, debug=self.debug, event_seq=event_seq, curr_event=curr_event)
                else:       # found item_id on server associated with curr_event
                    if self.debug:
                        print("Event " + str(curr_event.id) + " succeeds in finding " + str(curr_event.item_id) +
                              " in server " + str(curr_event.inserting_server))

                    # access the item, eventually initiates pull up procedure
                    self.access(item_id=curr_event.item_id, timestamp=curr_event.timestamp,
                                server_id=curr_event.inserting_server)
                    event_seq.update_del_timestamp(curr_event)      # update deleting timestamps
            elif curr_event.get_type() == "deleting":
                pass

    def serve_sequence_unbounded_cap(self, sequence, type):
        """
        Serve the sequence of requests passed as parameter.
        The parameter is used to create an event queue, on which the algo will work
        """
        queue = eh.create_queue(sequence=sequence, circle=self.circle, type=type)
        event_seq = copy.deepcopy(queue)  # deep copy = events are also duplicated (not just ref)
        print("Starting to work through event queue")
        while not event_seq.is_empty():
            curr_event = event_seq.delete()  # pop queue, event after event
            if curr_event.get_type() == "access":  # access event
                 self.access_mtf(item_id=curr_event.item_id, timestamp=curr_event.timestamp)

    def check_insertion_need(self, event):
        """ Iterate to server where the item has been hashed and check whether it is inserted
        If it is not, insert it
        """
        if self.debug:
            print("Checking insertion of " + str(event.item_id))
        parent = self.circle.root
        for i in range(0, len(self.circle.present_server_ids)):
            if self.circle.present_server_ids[i] >= self.circle.get_item_position(event.item_id):  # spot found
                self.check_item_status(parent, event.item_id, event.timestamp)  # make sure item is present
                return True
            # special case where we are trying to insert in a deleted server at end of circle
            elif (i == len(self.circle.present_server_ids) - 1) and (self.circle.get_item_position(event.item_id) != self.circle.present_server_ids[i]):
                raise Exception("Shouldn't happen in simple case")
                self.check_item_status(self.circle.root, event.item_id, event.timestamp)
                return True
            else:
                parent = parent.child_pointer  # iterate through circle

    def check_item_status(self, parent, item_id, timestamp):
        """
        Check the item status:
        If it is the first time it has been hashed to this server, record it and insert item
        If it has already been hashed, but not present, check whether it has been deleted (and evtl. re-insert)
        :param parent: server where item should be (original position)
        :param item_id: accessed item
        :param timestamp: access-timestamp
        """
        if item_id not in self.circle.hashed_items:
            self.circle.hashed_items.add(item_id)
            inserting_server = self.circle.insert(item_id)
            if self.circle.traditional_algo_failed:  # simple: we arrived at traditional failure
                pass
            if item_id in inserting_server.lru_list:
                raise Exception("Should not happen")
            inserting_server.lru_list.insert(0, item_id)
            inserting_server.item_timestamps[item_id] = timestamp
            if self.debug:
                print("First time-insertion of " + str(item_id) + " in " + str(inserting_server.id))
                print(f"lru: {inserting_server.lru_list}"
                      f"\nslots: {inserting_server.slots}"
                      f"\npresent servers: {self.circle.present_server_ids}")
            self.inserts_after_init += 1
            return True
        elif item_id in self.circle.deleted_items:  # item has been hashed to the circle before
            self.reinsert_removed_item(parent, item_id, timestamp)
            return True
        if self.debug:
            print("No insertion needed")

    def access_mtf(self, item_id, timestamp):
        original_server = self.circle.get_server(self.circle.get_item_position(item_id))
        steps_needed = 0
        most_recent_item = False
        for item_ids in original_server.slots:
            if original_server.item_timestamps[item_ids] > original_server.item_timestamps[item_id]:
                steps_needed += 1
        if steps_needed == 0:
            for item_ids in original_server.slots:
                if original_server.item_timestamps[item_ids] != original_server.item_timestamps[item_id]:
                    most_recent_item = True
                    break
            if not most_recent_item:
                steps_needed = random.randint(1, original_server.get_current_occupation())
        self.access_cost += steps_needed
        original_server.item_timestamps[item_id] = timestamp


    def access(self, item_id, timestamp, server_id):
        """
        Calculate the cost between original server and server where the item has been found
        """
        if self.debug:
            print("Found and accessing " + str(item_id) + " on server " + str(server_id))
        original_server = self.circle.get_server(self.circle.get_item_position(item_id))
        if not original_server:
            raise Exception(f"Failed getting a server for id={self.circle.get_item_position(item_id)}")
        n_iter = self.get_iterations(orig_server_id=original_server.id, curr_server_id=server_id)
        self.access_cost += n_iter      # add cost for finding item in server
        if n_iter > self.max_iteration:
            self.max_iteration = n_iter
        self.remove_item(parent=self.circle.get_server(server_id), item_id=item_id,
                         timestamp=timestamp, n_iteration=n_iter)
        if not n_iter == 0:
            if self.debug:
                print("Original server of " + str(item_id) + ": " + str(self.circle.get_item_position(item_id)) +
                      ". Pushing items from " + str(original_server.id) + " to " + str(server_id))
            self.iterate_and_push(parent=original_server, n_levels=n_iter)

            # update status of original server
            original_server.insert(item_id)
            original_server.item_timestamps[item_id] = timestamp
            if item_id in original_server.lru_list:
                raise Exception("Should not happen")
            original_server.lru_list.insert(0, item_id)  # insert at pos=0 because youngest timestamp
            if self.debug:
                print(f"Pulled up {item_id}, h = {self.circle.get_item_position(item_id)} "
                  f"to {original_server} from {self.circle.get_server(server_id)}")

    def reinsert_removed_item(self, parent, item_id, timestamp):
        """
        Check if item has been removed in the past because its access-timestamp surpassed the timeconstraint.
        If so, re-insert previously removed item.
        :param item_id: accessed item to be re-inserted
        :param parent: server where the item has been hashed originally
        :param timestamp: new timestamp to be recorded for this item
        """
        inserting_server = self.circle.insert(item_id=item_id)
        inserting_server.item_timestamps[item_id] = timestamp
        if item_id in inserting_server.lru_list:
            raise Exception(f"Inserting {item_id}. Should not happen")
        inserting_server.lru_list.insert(0, item_id)
        self.circle.deleted_items.remove(item_id)
        self.reinserted_items += 1
        if self.random_adjustment:
            self.circle.adjust_random_server_capacity(increase=True)
        if self.debug:
            print("Reinserted " + str(item_id) + " in " + str(inserting_server.id))

    def remove_item(self, parent, item_id, timestamp, n_iteration):
        """ Remove the item from the current server if n_iter > 1
        Otherwise, just update lru_list """
        if parent.check_for_item(item_id):  # accessing item found
            if item_id not in parent.lru_list:
                raise Exception(f"Item {item_id}, h={self.circle.get_item_position(item_id)}"
                                f" not in {parent.id}'s lru_list, slots: {parent.slots}!")
            parent.lru_list.remove(item_id)  # in any case, remove item from lru-list
            del parent.item_timestamps[item_id]  # and from timestamp-dict
            if n_iteration == 0:
                if item_id in parent.lru_list:
                    raise Exception("Should not happen")
                parent.lru_list.insert(0, item_id)  # if access at original server, just change lru-position, NO REMOVAL
                parent.item_timestamps[item_id] = timestamp
            else:
                parent.remove_item(item_id)
                if self.debug:
                    print(f"{n_iteration} btw. original and current: removed {item_id} from {parent}")
        else:
            raise Exception(f"Tried to remove {item_id} from server {parent.id} "
                            f"(hash={self.circle.get_item_position(item_id)}): item not found")

    def get_iterations(self, orig_server_id, curr_server_id) -> int:
        """
        get the number of steps required to reach from original/hashing server to server where item was found
        :param orig_server_id:
        :param curr_server_id:
        :return: number of steps
        """
        server = self.circle.root
        for i in range(0, len(self.circle.present_server_ids)):
            if self.circle.present_server_ids[i] == orig_server_id:
                n_steps = 0
                child = server
                if self.debug:
                    print(f"Iterating from server {child.id} to {curr_server_id}")
                for j in range(0, len(self.circle.present_server_ids)):     # do max. n_servers steps and count them
                    if child.id != curr_server_id:
                        n_steps += 1
                        child = child.child_pointer
                    else: return n_steps
                raise Exception("Could not compute distance btw. orig server and curr server")
            else:
                server = server.child_pointer

    def iterate_and_push(self, parent, n_levels):
        """
        Iterative approach, works with any # of servers
        Push down the LRU-item from the original server to the server n_levels forward in the circle"""
        while n_levels:
            child = parent.child_pointer

            # move item from the current server, if there is one
            if parent.lru_list:
                lru = parent.lru_list.pop()

                parent.remove_item(lru)
                if child.get_current_occupation() <= child.capacity:
                    child.insert(lru, buffer=True)      # necessary for the iterative approach
                elif child.get_current_occupation() < child.capacity:
                    child.insert(lru)
                    if self.debug:
                        print(f"Inserting {lru} in lru-list in server {child.id}")
                else:
                    raise Exception(f"Server {child.id} has more items than it's capable to keep")

                # update timestamps and insert in child lru-list
                lru_list_pos = self.update_timestamps(parent, child, lru)
                if self.debug:
                    print(f"Inserting {lru} in lru-list at pos {lru_list_pos} of server {child}")
                if lru in child.lru_list:
                    raise Exception("Should not happen")
                child.lru_list.insert(lru_list_pos, lru)
            parent = child
            n_levels -= 1

    def update_timestamps(self, parent, child, lru):
        """
        update parent and child timestamp-list
        :param parent: server from which item is pushed
        :param child: server that receives item
        :param lru: pushed item
        :return: the position of the pushed item in the lru-list of its new server
        """
        pos = 0
        if lru not in parent.item_timestamps:
            raise Exception(f"Item {lru} not in server {parent.id}'s lrus!")
        for i in child.item_timestamps:
            if parent.item_timestamps[lru] <= child.item_timestamps[i]:  # is lru older than the other child-items?
                pos += 1  # if older, position is higher (oldest at end of list)
        child.item_timestamps[lru] = parent.item_timestamps[lru]
        del parent.item_timestamps[lru]
        return pos